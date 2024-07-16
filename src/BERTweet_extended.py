import json
import logging
from loguru import logger

from transformers import AutoModel, AutoTokenizer
import torch.nn as nn
from BERTweet import *

NUM_CLASSES = 2

def init_weights(module):
    if type(module) in (nn.Linear, nn.Conv1d):
        nn.init.xavier_uniform_(module.weight)
    if type(module) == nn.LSTM:
        for param in module._flat_weights_names:
            if "weight" in param:
                nn.init.xavier_uniform_(module._parameters[param])

class BERT_CNN_LSTM(nn.Module):
    def __init__(self, bert_model_name=bert_model_name, cnn_out_channels=100, lstm_hidden_size=256):
        super(BERT_CNN_LSTM, self).__init__()
        self.bert = AutoModel.from_pretrained(bert_model_name).to(device)
        self.cnn = nn.Conv1d(in_channels=self.bert.config.hidden_size, out_channels=cnn_out_channels, kernel_size=3, padding=1)
        self.lstm = nn.LSTM(input_size=cnn_out_channels, hidden_size=lstm_hidden_size, batch_first=True)
        self.classifier = nn.Linear(lstm_hidden_size, NUM_CLASSES)

        self.apply(init_weights)

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        bert_output = bert_output.last_hidden_state.permute(0, 2, 1)  
        cnn_output = self.cnn(bert_output).permute(0, 2, 1)  
        lstm_output, _ = self.lstm(cnn_output)
        final_output = lstm_output[:, -1, :] 
        logits = self.classifier(final_output)
        return logits

class BERT_CNN_BiLSTM_enhanced(nn.Module):
    def __init__(self, bert_model_name=bert_model_name, cnn_out_channels=100, lstm_hidden_size=256):    
        super(BERT_CNN_BiLSTM_enhanced, self).__init__()
        self.bert = AutoModel.from_pretrained(bert_model_name).to(device)
        self.cnn = nn.Conv1d(in_channels=self.bert.config.hidden_size, out_channels=cnn_out_channels, kernel_size=3, padding=1)
        self.lstm = nn.LSTM(input_size=cnn_out_channels, hidden_size=lstm_hidden_size, batch_first=True, bidirectional=True)
        self.attention = Attention(lstm_hidden_size * 2)
        self.dropout = nn.Dropout(p=0.3)
        self.layer_norm = nn.LayerNorm(lstm_hidden_size * 2)
        self.classifier = nn.Linear(lstm_hidden_size * 2, NUM_CLASSES)
        self.apply(init_weights)

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        bert_output = bert_output.last_hidden_state.permute(0, 2, 1)  # (batch_size, hidden_size, sequence_length)
        cnn_output = self.cnn(bert_output).permute(0, 2, 1)  # (batch_size, sequence_length, cnn_out_channels)
        lstm_output, _ = self.lstm(cnn_output)
        attention_output = self.attention(lstm_output)
        dropout_output = self.dropout(attention_output)
        final_output = self.layer_norm(dropout_output)
        logits = self.classifier(final_output)
        return logits

class Attention(nn.Module):
    def __init__(self, hidden_size):
        super(Attention, self).__init__()
        self.attention = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, lstm_output):
        weights = self.attention(lstm_output).squeeze(-1)
        weights = torch.softmax(weights, dim=1)
        output = torch.bmm(weights.unsqueeze(1), lstm_output).squeeze(1)
        return output
def load_checkpoint(model, checkpoint_path):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    return model

config_path = './config.json'
config, bert_model_name, device, dataset, test_dataset, tokenizer = setup_environment(config_path)

model = BERT_CNN_LSTM()

#replace model with checkpoint model if checkpoint is provided and asked for
checkpoint_path = config["checkpoint_path"] 
if config["load_checkpoint"] and  os.path.exists(checkpoint_path):
    model = load_checkpoint(model, checkpoint_path).to(device)
    logger.info(f'Model loaded from checkpoint: {checkpoint_path}')
    

dataset, test_dataset, data_collator = prepare_datasets(dataset, test_dataset)

train_and_predict(model, dataset, test_dataset, data_collator)

exit(0)