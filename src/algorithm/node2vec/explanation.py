import numpy as np

text = "natural language processing and machine learning is fun and exciting"

# Note the .lower() as upper and lowercase does not matter in our implementation
# [['natural', 'language', 'processing', 'and', 'machine', 'learning', 'is', 'fun', 'and', 'exciting']]
corpus = [[word.lower() for word in text.split()]]

setting = {
    'window_size': 2,
    'n': 10,  # dimensions of word embeddings, also refer to size of hidden layer
    'epochs': 50,
    'learning_rate': 0.01
}


def run():
    w2v = word2vec()
    training_data = w2v.generate_training_data(setting, corpus)
    w2v.train(training_data)


class word2vec():
    def __init__(self):
        self.n = setting['n']
        self.lr = setting['learning_rate']
        self.epochs = setting['epochs']
        self.window = setting['window_size']

    def word2onehot(self, word):
        """
        word_vec - initialise a blank vector
        Khởi tạo vectơ 0 với số chiều là số từ trong từ điển
        """
        word_vec = [0 for i in range(0, self.v_count)]
        """
        Get ID of word from word_index
        """
        word_index = self.word_index[word]
        """
        Change value from 0 to 1 according to ID of the word
        """
        word_vec[word_index] = 1
        return word_vec

    def generate_training_data(self, setting, corpus):
        from collections import defaultdict
        # Find unique word counts using dictonary
        word_counts = defaultdict(int)
        for row in corpus:
            for word in row:
                word_counts[word] += 1

        # How many unique words in vocab? 9
        """
        v_count: The length of Vocabulary (the unique words in the corpus)
        """
        self.v_count = len(word_counts.keys())
        """
        words_list: The list of words in Vocabulary
        """
        self.words_list = list(word_counts.keys())
        """
        word_index: <dict>{'word':'index'}
        """
        self.word_index = dict((word, i)
                               for i, word in enumerate(self.words_list))
        """
        index_word: <dict>{'index':'word'}
        """
        self.index_word = dict((i, word)
                               for i, word in enumerate(self.words_list))

        training_data = []
        """
        Cycle through each sentence in corpus
        """
        for sentence in corpus:
            sentence_len = len(sentence)
            """
            Cycle through each word in sentence
            """
            for i, word in enumerate(sentence):
                """
                Convert target word to one-hot
                """
                w_target = self.word2onehot(word)
                """
                Cycle through context window
                """
                w_context = []
                """
                Note: window_size 2 will have range of 5 values
                """
                for j in range(i - self.window, i + self.window+1):
                    """
                    Criteria for context word 
                      1. Target word cannot be context word (j != i)
                      2. Index must be greater or equal than 0 (j >= 0) 
                      - if not list index out of range
                      3. Index must be less or equal than length of sentence (j <= sentence_len-1) 
                      - if not list index out of range 
                    """
                    if ((j != i) and (j >= 0) and (j <= sentence_len-1)):
                        """
                        Append the one-hot representation of word to w_context
                        """
                        w_context.append(self.word2onehot(word))

                """
                  training_data contains a one-hot representation of the
                target word and context words
                """
                training_data.append([w_target, w_context])

        return np.array(training_data)

    def train(self, training_data):
        """
        + Initialising weight matrices
        + Both s1 and s2 should be randomly initialised 
        but for this demo, we pre-determine the arrays (getW1 and getW2)
        + getW1 - shape (9x10) and getW2 - shape (10x9)
        + Tại sao cần khởi tạo w1 và w2 là giá trị từ -1 đến 1
        """
        self.w1 = np.array(getW1)
        self.w2 = np.array(getW2)
        # self.w1 = np.random.uniform(-1, 1, (self.v_count, self.n))
        # self.w2 = np.random.uniform(-1, 1, (self.n, self.v_count))
