# Transformer / Universal Transformer

Transformer ('Attention is all you need' A. Vaswani et el.)

Universal Transformer ('Universal Transformer' M. Dehghani et. el)

## Requirements

python 3.6

pytorch 1.3

## To run

check Examples/


---

## The Change Made to this Repository

* Comment out the unused import
* Remove the `.to(device=device)` in `models/Act.py`
* Add the `.gitignore` file

The `models/Enc.py Encoder` can run properly with Python 3.7 and PyTorch 1.5 (CPU).
