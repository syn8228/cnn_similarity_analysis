import argparse
from lib.io import read_config
#EXP_PATH = "/cluster/yinan/yinan_cnn/cnn_similarity_analysis/experiments/the_MET/experiment_2022-01-24_14-25-41/"
EXP_PATH = "/cluster/yinan/yinan_cnn/cnn_similarity_analysis/experiments/artdl/experiment_2022-01-15_15-16-02/"
#EXP_PATH = "/cluster/yinan/yinan_cnn/cnn_similarity_analysis/experiments/photoart50/experiment_2022-04-21_11-21-02/"
# EXP_PATH = "/cluster/yinan/yinan_cnn/cnn_similarity_analysis/experiments/iconart/experiment_2022-05-13_17-56-06/"
EXP_PARAMS = read_config(EXP_PATH + "experiment_parameters.json")

def siamese_args():
    parser = argparse.ArgumentParser()

    def aa(*args, **kwargs):
        group.add_argument(*args, **kwargs)

    group = parser.add_argument_group('feature extraction options')
    aa('--mining_mode', default="offline", help="online or offline data mining")
    aa('--transpose', default=-1, type=int, help="one of the 7 PIL transpose options ")
    aa('--train', default=False, action="store_true", help="run Siamese training")
    aa('--pca', default=False, action="store_true", help="use pca or not")
    aa('--start', default=False, action="store_true", help="run Siamese training without lodading checkpoint")
    aa('--track2', default=False, action="store_true", help="run feature extraction for track2")
    aa('--device', default="cuda:0", help='pytroch device')
    aa('--batch_size', default=EXP_PARAMS['training']['batch_size'], type=int, help="max batch size to use for extraction")
    aa('--num_workers', default=EXP_PARAMS['num_workers'], type=int, help="nb of dataloader workers")
    aa('--optimizer', default="sgd", help='type of optimizer')
    aa('--loss', default="normal", help='type of loss strcture')
    aa('--method', default=None, help='type of experiment method')

    group = parser.add_argument_group('model options')
    aa('--model', default=EXP_PARAMS['model']['model_name'], help="model to use")
    aa('--pca_file', default=None, help="path to saved pca file")
    aa('--checkpoint', default='Triplet_best.pth', help='best saved model name')
    aa('--GeM_p', default=7.0, type=float, help="Power used for GeM pooling")
    aa('--scales', default="1.0", help="scale levels")
    aa('--imsize', default=EXP_PARAMS['dataset']['image_size'], type=int, help="max image size at extraction time")
    aa('--lr', default=EXP_PARAMS['training']['learning_rate'], type=float, help="learning rate")
    aa('--momentum', default=EXP_PARAMS['training']['momentum'], type=float,
       help="momentum for sgd")
    aa('--weight_decay', default=0.0, type=float, help="max image size at extraction time")
    aa('--margin', default=10.0, type=float, help="margin in loss function")
    aa('--regular', default=0.01, type=float, help="regularization factor in custom loss function")
    aa('--threshold_d', default=8.0, type=float, help="threshold for confusion_matrix with euclidean distance")
    aa('--threshold_s', default=8.0, type=float, help="threshold for confusion_matrix with cosine similarity")
    aa('--pca_dim', default=256, type=int, help="output dimensionality of pca")

    group = parser.add_argument_group('dataset options')
    aa('--train_dataset', default=EXP_PARAMS['dataset']['dataset_name'], help="training dataset name")
    aa('--val_dataset', default=EXP_PARAMS['dataset']['dataset_name'], help="validation dataset name")
    aa('--test_dataset', default=EXP_PARAMS['dataset']['dataset_name'], help="test dataset name")
    aa('--data_path', default=EXP_PARAMS['dataset']['data_path'], help="Path to dataset folder")
    aa('--database_path', default=EXP_PARAMS['dataset']['database_path'], help="Path to images folder")
    aa('--d1', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/D1/', help="folder for d1 subset")
    aa('--d2', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/D2/', help="folder for d2 subset")
    aa('--d3', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/D3/', help="folder for d3 subset")
    aa('--p1', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/P1/', help="folder for p1 subset")
    aa('--p2', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/P2/', help="folder for p2 subset")
    aa('--p3', default='/cluster/shared_dataset/ImageCollation/ManuscriptDownloader/download/P3/', help="folder for p3 subset")
    aa('--query_list', default=None, help="file with query image filenames")
    aa('--gt_list', default=None, help="file or folder with ground truth image filenames")
    aa('--train_list', default=None, help="file with training image filenames")
    aa('--db_list', default=None, help="file with reference image filenames")
    aa('--val_list', default=None, help="file with validation image filenames")
    aa('--test_list', default=None, help="file with test image filenames")
    aa('--image_data', default=None, help="path to images")
    aa('--len', default=1000, type=int, help="nb of training vectors for the SiameseNetwork")
    aa('--num_epochs', default=EXP_PARAMS['training']['num_epochs'], type=int, help="nb of training epochs for the SiameseNetwork")
    aa('--i0', default=0, type=int, help="first image to process")
    aa('--i1', default=-1, type=int, help="last image to process + 1")

    group = parser.add_argument_group('output options')
    aa('--exp_path', default=EXP_PATH, help="path to experiment folder")
    aa('--query_f', default="isc2021/data/query_siamese.hdf5", help="write query features to this file")
    aa('--db_f', default="isc2021/data/db_siamese.hdf5", help="write query features to this file")
    aa('--train_f', default="isc2021/data/train_siamese.hdf5", help="write training features to this file")
    aa('--full_f', default="isc2021/data/full_siamese.hdf5", help="write full features to this file")
    aa('--matched_f', default=None, help="save matched result to this folder")
    aa('--test_f', default=None, help="save test result to this folder")
    aa('--net', default=EXP_PATH + 'models/', help="save network parameters to this folder")
    aa('--plots', default=EXP_PATH + 'plots/', help="save visualized test result to this folder")
    aa('--save_model', default='best.pth', help="name of the saved cehckpoint")
    aa('--p1_f', default=None, help="write p1 features to this file")
    aa('--p2_f', default=None, help="write p2 features to this file")
    aa('--p3_f', default=None, help="write p3 features to this file")
    aa('--d1_f', default=None, help="write d1 features to this file")
    aa('--d2_f', default=None, help="write d2 features to this file")
    aa('--d3_f', default=None, help="write d3 features to this file")

    group = parser.add_argument_group('optuna parameters')
    aa('--upper_bound', type=float, default=None, help="upper bound of the hyperparameter")
    aa('--lower_bound', type=float, default=None, help="lower bound of the hyperparameter")
    aa('--num_experiment', default=20, type=int, help="number of search experiments")

    args = parser.parse_args()
    args.scales = [float(x) for x in args.scales.split(",")]

    print("args=", args)

    return args