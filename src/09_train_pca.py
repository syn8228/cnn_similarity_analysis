import sys
sys.path.append('/cluster/yinan/yinan_cnn/cnn_similarity_analysis/')
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import time
from torch.utils.data import DataLoader
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity
from src.lib.siamese.args import siamese_args
from src.lib.siamese.model import load_siamese_checkpoint, TripletSiameseNetwork, TripletSiameseNetwork_custom
from src.data.siamese_dataloader import ImageList
from src.lib.siamese.dataset import get_transforms
from lib.io import read_config
from lib.metrics import calculate_distance
import faiss
import random


def generate_features(args, net, image_names, data_loader):
    features_list = list()
    # images_list = image_names
    if args.loss == 'normal':
        t0 = time.time()
        with torch.no_grad():
            for no, data in enumerate(data_loader):
                images = data
                images = images.to(args.device)
                feats = net.forward_once(images)
                features_list.append(feats.cpu().numpy())
                # images_list.append(images.cpu().numpy())
        t1 = time.time()
    elif args.loss == 'custom':
        t0 = time.time()
        with torch.no_grad():
            for no, data in enumerate(data_loader):
                images = data
                images = images.to(args.device)
                feats1, feats2, feats3, feats4, feats5 = net.forward_once(images)
                features_list.append(feats5.cpu().numpy())
                # images_list.append(images.cpu().numpy())
        t1 = time.time()
    features = np.vstack(features_list)
    print(f"image_description_time: {(t1 - t0) / len(image_names):.5f} s per image")
    return features


def train(args):
    if args.device == "gpu":
        print("hardware_image_description:", torch.cuda.get_device_name(0))

    if args.train_dataset == "image_collation":
        d1_images = [args.d1 + 'illustration/' + l.strip() for l in open(args.d1 + 'files.txt', "r")]
        d2_images = [args.d2 + 'illustration/' + l.strip() for l in open(args.d2 + 'files.txt', "r")]
        d3_images = [args.d3 + 'illustration/' + l.strip() for l in open(args.d3 + 'files.txt', "r")]

        train_images = d1_images + d2_images + d3_images

    if args.train_dataset == 'isc2021':
        rs = np.random.RandomState()
        TRAIN = '/cluster/shared_dataset/isc2021/training_images/training_images/'
        train_images = [TRAIN + l.strip() + '.jpg' for l in open(args.train_list, "r")]
        train_images = [train_images[i] for i in rs.choice(len(train_images), size=10000, replace=False)]

    if args.train_dataset == 'artdl':
        train = pd.read_csv(args.train_list)
        train_images = list(train['anchor_query']) + list(train['ref_positive']) + list(train['ref_negative'])

    transforms = get_transforms(args)
    train_dataset = ImageList(train_images, transform=transforms)
    train_loader = DataLoader(dataset=train_dataset, shuffle=True, num_workers=args.num_workers,
                              batch_size=args.batch_size)
    if args.loss == 'normal':
        net = TripletSiameseNetwork(args.model, args.method)
    elif args.loss == 'custom':
        net = TripletSiameseNetwork_custom(args.model)
    if args.net:
        state_dict = torch.load(args.net + args.checkpoint)
        net.load_state_dict(state_dict)
    net.to(args.device)
    net.eval()

    train_features = generate_features(args, net, train_images, train_loader)

    d = train_features.shape[1]
    pca = faiss.PCAMatrix(d, args.pca_dim, -0.5)
    print(f"Train PCA {pca.d_in} -> {pca.d_out}")
    pca.train(train_features)
    save_path = args.net + args.pca_file
    print(f"Storing PCA to {save_path}")
    faiss.write_VectorTransform(pca, save_path)

    if args.val_dataset == 'image_collation':
        d1_images = [args.d1 + 'illustration/' + l.strip() for l in open(args.d1 + 'files.txt', "r")]
        d2_images = [args.d2 + 'illustration/' + l.strip() for l in open(args.d2 + 'files.txt', "r")]
        d3_images = [args.d3 + 'illustration/' + l.strip() for l in open(args.d3 + 'files.txt', "r")]

        val_images = d1_images + d2_images + d3_images
        val_dataset = ImageList(val_images, transform=transforms)
        val_loader = DataLoader(dataset=val_dataset, shuffle=False, num_workers=args.num_workers,
                                batch_size=args.batch_size)
        val_features = generate_features(args, net, val_images, val_loader)

        if args.pca:
            d1_features = pca.apply_py(val_features[:len(d1_images)])
            d2_features = pca.apply_py(val_features[len(d1_images): len(d1_images)+len(d2_images)])
            d3_features = pca.apply_py(val_features[len(d1_images)+len(d2_images): len(train_features)])
        else:
            d1_features = val_features[:len(d1_images)]
            d2_features = val_features[len(d1_images): len(d1_images)+len(d2_images)]
            d3_features = val_features[len(d1_images)+len(d2_images): len(train_features)]

        gt_d1d2 = read_config(args.gt_list + 'D1-D2.json')
        gt_d2d3 = read_config(args.gt_list + 'D2-D3.json')
        gt_d1d3 = read_config(args.gt_list + 'D1-D3.json')

        dp_d1d2, dn_d1d2, sp_d1d2, sn_d1d2 = calculate_distance(gt_d1d2, d1_features, d2_features)
        dp_d2d3, dn_d2d3, sp_d2d3, sn_d2d3 = calculate_distance(gt_d2d3, d2_features, d3_features)
        dp_d1d3, dn_d1d3, sp_d1d3, sn_d1d3 = calculate_distance(gt_d1d3, d1_features, d3_features)

        mean_dp = np.mean(np.array(dp_d1d2 + dp_d2d3 + dp_d1d3))
        mean_dn = np.mean(np.array(dn_d1d2 + dn_d2d3 + dn_d1d3))
        mean_sp = np.mean(np.array(sp_d1d2 + sp_d2d3 + sp_d1d3))
        mean_sn = np.mean(np.array(sn_d1d2 + sn_d2d3 + sn_d1d3))


    elif args.val_dataset == 'artdl':
        val = pd.read_csv(args.val_list)
        query_val = list(val['anchor_query'])
        p_val = list(val['ref_positive'])
        n_val = list(val['ref_negative'])
        query_val_list = ImageList(query_val, transform=transforms)
        p_val_list = ImageList(p_val, transform=transforms)
        n_val_list = ImageList(n_val, transform=transforms)
        query_val_loader = DataLoader(dataset=query_val_list, shuffle=False, num_workers=args.num_workers,
                                      batch_size=args.batch_size)
        p_val_loader = DataLoader(dataset=p_val_list, shuffle=False, num_workers=args.num_workers,
                                  batch_size=args.batch_size)
        n_val_loader = DataLoader(dataset=n_val_list, shuffle=False, num_workers=args.num_workers,
                                  batch_size=args.batch_size)
        query_val_features = generate_features(args, net, query_val, query_val_loader)
        p_val_features = generate_features(args, net, p_val, p_val_loader)
        n_val_features = generate_features(args, net, n_val, n_val_loader)

        if args.pca:
            query_val_features = pca.apply_py(query_val_features)
            p_val_features = pca.apply_py(p_val_features)
            n_val_features = pca.apply_py(n_val_features)

        mean_dp = np.mean(np.diag(euclidean_distances(query_val_features, p_val_features)))
        mean_dn = np.mean(np.diag(euclidean_distances(query_val_features, n_val_features)))
        mean_sp = np.mean(np.diag(cosine_similarity(query_val_features, p_val_features)))
        mean_sn = np.mean(np.diag(cosine_similarity(query_val_features, n_val_features)))

    print('average positive distance: {}'.format(mean_dp))
    print('average negative distance: {}'.format(mean_dn))
    print('\n')
    print('average positive similarity: {}'.format(mean_sp))
    print('average negative similarity: {}'.format(mean_sn))

if __name__ == "__main__":

    pca_args = siamese_args()
    if pca_args.device == "cuda:0":
        print("hardware_image_description:", torch.cuda.get_device_name(0))

    train(pca_args)














