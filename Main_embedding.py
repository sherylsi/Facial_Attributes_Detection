import json
from Classes.LoadModel import BaseModel
from Classes.Predict import Prediction
from config import *
from Classes.Train import *
from Classes.Summarize import *
from Classes.BaseCls import *
import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop, Adam


def main(label, exp=True):
    # Start images processing and dataframe splitting
    trainer = Train(IND_FILE, IMAGE_PATH)
    print('Reading File...\nCreating Train, Test...')

    print(f'Train on {label} attribute')
    train, test = trainer.data_preprocess(IND_FILE, label, 400, True, None)
    print('Done!')

    # Loading Base Model
    print(f'\nLoading Model...')
    model_list = ['vgg19', 'MobileNetV2', 'vggface', 'facenet', 'emotion', 'age', 'gender', 'race']
    model_name = 'facenet'  # input('Choose one model to load: )

    # Training
    basemodel = BaseModel(model_name)
    model = basemodel.load_model(True)

    print(f'\nSave embedding...')
    X_train, y_train = basemodel.loading_embedding(IMAGE_PATH, model, train, 1)
    X_test, y_test = basemodel.loading_embedding(IMAGE_PATH, model, test, 1)

    print('Running Grid Search on Cls...')
    df_cls = gridsearch_cls(X_train, y_train, X_test, y_test, MLA)
    print(df_cls.iloc[:, :-1])

    # Plot top classifier
    if not exp:
        plot_best_model(df_cls)

    name_best_model = df_cls['MLA Name'].values[0]

    # Optimizing
    print('Starting hyper_parameters GridSearch...\n')
    top_cls = gridsearch_params(df_cls, X_train, y_train)
    print(top_cls['param'])

    print('Test for best classifier...')
    df_top_cls = gridsearch_cls(X_train, y_train, X_test, y_test, top_cls)
    print(df_top_cls.iloc[:, :-1], '-'*50, sep='\n')

    best_model = [i for i in top_cls['param'] if str(i).startswith(df_top_cls['MLA Name'].values[0])]

    cls = str(best_model).strip('[]')
    print(f'Best Model:\n{cls}\n', '-'*50,)
    best_cls = cls
    y_pred = df_top_cls['MLA pred'].values[0]

    if not exp:
        # plot confusion matrix and acc score
        ax = plt.subplot(1, 1, 1)
        cm = confusion_matrix(y_test, y_pred) / len(y_test)
        accuracy = accuracy_score(y_test, df_top_cls['MLA pred'].values[0])
        sns.heatmap(cm, annot=True, cmap='Wistia', ax=ax)
        plt.title(f'{name_best_model}\n\nAccuracy: {accuracy * 100:.2f}')
        plt.ylabel('True')
        plt.xlabel('Predicted')
        plt.show()

    # print("Checking XGB best params:")
    # check_xgb(feature_train, label_train)
    # model = eval(best_cls)
    # get_model_results(model, X_train, X_test, y_train, y_test)


if __name__ == '__main__':
    labels = ['Eyeglasses']
    for label in labels:
        main(label, False)
