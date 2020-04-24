# LaLigaPredictor

As of now, all data is in <i>data.csv</i>. Train will (N-10) all samples, and predict outcome for last 10 samples.

Main program, <i>LaLigaPredictor.py</i> processes, cleans data and use a MLP classifier to decide outcome of unknown matches. We run the classifier several times to try different random-states, so we end up with a probability of each outcome (1, X, 0). If the probability of one of them is larger than a threshold confidence value, we accept result
