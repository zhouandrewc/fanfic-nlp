'''
# Separate function to fine-tune the GTP-2 model
#
# Andrew Zhou
#
'''

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, default_data_collator
import sys
sys.path.append("..")
from util.generate import FicDataset, EarlyStoppingCallback

train_dataset = torch.load("../data/datasets/train.data")
val_dataset = torch.load("../data/datasets/val.data")

tokenizer = GPT2Tokenizer.from_pretrained("../models/tokenizer_textgen")
model = GPT2LMHeadModel.from_pretrained("gpt2")

model.resize_token_embeddings(len(tokenizer))
training_args = TrainingArguments(
    output_dir='../models/checkpoints',          # output directory
    overwrite_output_dir = True,
    save_total_limit = 3,
    num_train_epochs = 5,              # total # of training epochs
    per_device_train_batch_size=2,  # batch size per device during training
    per_device_eval_batch_size=2,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    save_steps=500,
    weight_decay=0.01,               # strength of weight decay
    logging_dir='../models/logs',            # directory for storing logs
    evaluation_strategy="steps",
    logging_steps=500,
    eval_steps=500,
    load_best_model_at_end=True,
)

callback = EarlyStoppingCallback()

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset,            # evaluation dataset
    tokenizer=tokenizer,
    data_collator = default_data_collator,

    callbacks=[callback]
)

trainer.train()

model.save_pretrained("../models/model_textgen")