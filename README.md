# Text Classification 2024

## Computational Intelligence Laboratory Project 

Our text classification pipeline is broken into the following segments for modularity:
1. Data Analysis and Vizualization
2. Data Preprocessing
3. Training Model and Generating Predictions
4. Combining Predictions

Throughout our systematic and research oriented approach, we tried out various preprocessing techniques, models - each with various hyperparameter configurations. Hence, we decided to breakup the pipeline as above, allowing us to combine predictions generated using different methods into a final prediction in Step 4. 

## Setup Instructions

Create a virtual environment if you desire, and then run the following command in the home directory to install all the required packages. There are two parts in this file - one set of packages for the classical method code and the other set of packages for the deep learning approach. 

```pip install -r requirements.txt```

## Data Analysis

Run the analysis.ipynb file to see a vizualization of the dataset and get an idea about the distribution of hashtags, emoticons, etc.

## Preprocessing
TODO

The neg-pos.py file consists of all the preprocessing discussed in the paper. Apart from the default settings, other options can be enabled using the flags. For example, if you want to replace the abbreviations with their full forms, you only need to set the ABBREV flag to True and then generate the preprocessed dataset. The paths to the preprocessed dataset and test data are already added to the config file. segmentHashtags.py is a separate file that is used to break up the words in a hashtag to take that sentiment into account.



## Baselines

### Classical ML Methods:
TODO

We begin this project by trying out the classical algorithms such as SVC, Logistic Regression, Bernoulli and Random Forest. Different types of embeddings are used such as Bag of Words, TF-IDF, Word2Vec and Sentence Embeddings. classical.py has all the models and respective training snippets using all types of embeddings. All other models can be commented out apart from the desired model and embedding type. The accuracies are appended to a txt file and the predictions are saved to a csv file. Moreover, for large datasets (with 1M tweets) batch processing is also included.

### Deep Learning Based - BERTweet:

For our deep learning baselines, we fine-tune the BERTweet model [[1]](#1).
The script for the same is provided in [BERTweet.py](./src/3-Models/BERTweet.py).
To train the model and generate predictions with early stopping criteria, modify the following in [``config.json``](./src/config.json) to adjust training parameters and data and output folders accordingly:

```
    "output_dir": <PATH TO SAVE MODEL CHECKPOINTS AND FINAL PREDICTIONS>,
    "neg_training_path": <PATH TO NEGATIVE TRAINING SET>
    "pos_training_path": <PATH TO POSITIVE TRAINING SET>
    "test_path": <PATH TO TEST SET>
    "load_checkpoint": false, --- set to true if loading from a checkpoint and set path in "checkpoint_path"
    "checkpoint_path": "", --- Provide path to checkpoint folder if restarting training from a checkpoint
    "eval_freq": 5, --- no of time validation accuracy is computed per epoch
    "test_size": 0.1 --- size of validation dataset
```
After modifying the config, make sure to navigate into the [``./src/3-Models``](./src/3-Models) folder before running the following command.

```python3 BERTweet.py```

The final prediction probabilities and labels will be saved in the output directory specified in the [``config.json``](./src/config.json) as ``probabilities.csv`` and ``final_predictions.csv`` respectively. 
To fine-tune the model using a pre-processed dataset, simply change the corresponding paths to the training and test set in the [``config.json``](./src/config.json).


## BERTweetConvFusionNet

_BERTweetConvFusionNet_, our novel architecture, is a Convolutional Recurrent Neural Network or CRNN-based 'fusion net', notable for its ability to to capture local and sequential patterns and context in the text data, leading to better performance in sentiment classification. Building on previous work [[2]](#2), our novel introduction is the addition of an Attention layer. We also try out both Bi-LSTM and LSTM alongwith 1D and 2D CNN layers. 
Various configuations can be built and fine-tuned using [BERTweet_extended.py](./src/3-Models/BERTweet_extended.py). 

![Picture of architecture of BERTweetConvFusionNet](https://github.com/user-attachments/assets/4bf00797-694a-4293-86f3-6b748565fb40)


You can choose between the following options for the novel architecture and set these strings in the [``config.json``](./src/config.json). The default model used is a ``2dCNN_biLSTM``. All other model parameters such as ``epoch`` and ``batch_size`` can be modified similarly [BERTweet.py](./src/3-Models/BERTweet.py).
```
"model_name": "2dCNN_biLSTM" 
```

- ``1dCNN_LSTM``: to use the BERTweet embeddings with a 1D-CNN and uni-directional LSTM
- ``2dCNN_LSTM``: to use the BERTweet embeddings with a 2D-CNN and uni-directional LSTM
- ``2dCNN_biLSTM``: to use the BERTweet embeddings with a 2D-CNN and bi-directional LSTM
- ``2dCNN_LSTM_Attn``: to use the BERTweet embeddings with a 2D-CNN and uni-directional LSTM, followed by an attention layer
- ``2dCNN_biLSTM_Attn``: to use the BERTweet embeddings with a 2D-CNN and bi-directional LSTM, followed by an attention layer

After modifying the config, make sure to navigate into the [``./src/3-Models``](./src/3-Models) folder before running the following command to train the model and generate predictions.

```python3 BERTweet_extended.py```

## Ensembling

We provide an ensembling script in [ensemble.py](./src/4-Ensemble/ensemble.py) to ensemble the final predicted probabilities of two or more models. Before running this script, simply add the paths of all the files with the probabilities in the [``config.json``](./src/config.json) as shown below:

```
"prediction_paths": [
    <PATH TO PROBABILITIES_FROM_MODEL_1.csv>,
    <PATH TO PROBABILITIES_FROM_MODEL_2.csv>,
    ...
]
```
### Reproducing the best classification accuracy
To achieve the best score, load the probabilities.csv of all the models into the config (you have to change the paths to match your folder structure).

Example config for the best performing ensemble which consisted of the following models:
1. Fine-tuned BERTweet without pro-processing
2. Fine-tuned BERTweet with best pre-processing (Basic + emoticon pre-processing)
3. BERTweetConvFusionNet with `2dCNN_biLSTM` configuration
4. BERTweetConvFusionNet with `2dCNN_biLSTM_Attn` configuration
```
"prediction_paths": [
    "/home/laschulz/cil-project/data/final_table/BERT_2DCNN_BiLSTM_Attn/prob.csv",
    "/home/laschulz/cil-project/data/final_table/no_pre/prob.csv",
    "/home/laschulz/cil-project/data/final_table/bertweet_best_preprocessing/prob.csv",
    "/home/laschulz/cil-project/data/final_table/BERT_2DCNN_BiLSTM/prob.csv"
]
```


### Contributors:
- Debeshee
- Laura
- Mariia
- Piyushi




## References
<a id="1">[1]</a> 
Nguyen, Dat Quoc, Thanh Vu, and Anh Tuan Nguyen. "BERTweet: A pre-trained language model for English Tweets." arXiv preprint arXiv:2005.10200 (2020).


<a id="2">[2]</a> 
Kokab, Sayyida Tabinda, Sohail Asghar, and Shehneela Naz. "Transformer-based deep learning models for the sentiment analysis of social media data." Array 14 (2022): 100157.
