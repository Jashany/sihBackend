import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
import math
import numpy as np
import re
import operator
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.corpus.reader.wordnet import WordNetError
import nltk
nltk.download('punkt')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

df_vec = {}
doc_w_vec = {}
total_docs = 1  # Single document processing
legal_words = []


def read_legal_dict(dict_path):
    with open(dict_path, "r") as l_f:
        for wd in l_f:
            legal_words.append(wd.strip())


def cal_df(input_text):
    global df_vec
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sntncs = tokenizer.tokenize(input_text)
    wordnet_lemmatizer = WordNetLemmatizer()
    stop = set(stopwords.words('english'))

    nor_stp_lmt = []
    for s in sntncs:
        s_nor_stp_lmt = ""
        s = s.lower()
        words = word_tokenize(s)
        for w in words:
            if w not in stop:
                w = wordnet_lemmatizer.lemmatize(w)
                s_nor_stp_lmt = s_nor_stp_lmt + w + " "
        nor_stp_lmt.append(s_nor_stp_lmt)

    unq_words = {}
    for s in nor_stp_lmt:
        for w in word_tokenize(s):
            if w != ".":
                if w not in unq_words:
                    unq_words[w] = 0

    for k in unq_words.keys():
        if k in df_vec:
            df_vec[k] += 1
        else:
            df_vec[k] = 1


def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if isinstance(i, Tree):
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
            else:
                current_chunk = []
    return continuous_chunk


def cal_tf_Idf(input_text, dict_path, word_limit, sentence_limit):
    global legal_words
    global total_docs
    global doc_w_vec
    global df_vec

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sntncs = tokenizer.tokenize(input_text)

    wordnet_lemmatizer = WordNetLemmatizer()
    stop = set(stopwords.words('english'))

    nor_stp_lmt = []
    stp_lmt_cased = []
    for s in sntncs:
        s_nor_stp_lmt = ""
        s_u = s.lower()
        words = word_tokenize(s_u)
        for w in words:
            if w not in stop:
                w = wordnet_lemmatizer.lemmatize(w)
                s_nor_stp_lmt += w + " "
        nor_stp_lmt.append(s_nor_stp_lmt)

        words = word_tokenize(s)
        case_sntnc = ""
        for w in words:
            if w not in stop:
                w = wordnet_lemmatizer.lemmatize(w)
                case_sntnc += w + " "
        stp_lmt_cased.append(case_sntnc)

    tf_vec = {}
    length = 0
    for i in range(len(nor_stp_lmt)):
        s = nor_stp_lmt[i]
        for w in word_tokenize(s):
            if w != ".":
                length += 1
                tf_vec[w] = tf_vec.get(w, 0) + 1

    tf_idf_doc = {}
    for k, v in tf_vec.items():
        tf_vec[k] = float(v) / float(length)
        tf_idf_doc[k] = tf_vec[k] * math.log10(float(total_docs) / float(df_vec[k]))

    doc_w_vec[input_text] = tf_idf_doc

    tf_idf_sntnc = {}
    std_list = []
    all_cased_s = " ".join(stp_lmt_cased)
    all_ne_list = get_continuous_chunks(all_cased_s)
    ne_dict = {s: [] for s in sntncs}
    for ne in all_ne_list:
        for s in sntncs:
            if ne in s:
                ne_dict[s].append(ne)

    for i in range(len(nor_stp_lmt)):
        s = nor_stp_lmt[i]
        ac_s = sntncs[i]
        sm = sum(tf_idf_doc.get(w, 0) for w in word_tokenize(s))
        no_of_words = len(word_tokenize(s))
        if no_of_words == 0:
            continue
        tf_idf_s = float(sm) / float(no_of_words)
        tf_idf_sntnc[ac_s] = tf_idf_s
        std_list.append(tf_idf_s)

    sd = np.std(std_list)
    for i, s in enumerate(nor_stp_lmt):
        cased_s = stp_lmt_cased[i]
        ne_list = ne_dict[sntncs[i]]
        ac_s = sntncs[i]
        if len(word_tokenize(s)) != 0:
            e = float(len(ne_list)) / float(len(word_tokenize(s)))
        else:
            e = 0
        op = any(char.isdigit() for char in s)
        d = 1 if op else 0
        words = word_tokenize(s)
        bag = []
        for wd in words:
            try:
                r = re.compile(wd + ".*")
            except:
                continue
            newlist = list(filter(r.match, legal_words))
            for item in newlist:
                if item in s:
                    bag.extend(item.split(" "))
        myset = set(bag)
        g = float(len(myset)) / float(len(words)) if len(words) > 0 else 0

        tf_idf_sntnc[ac_s] += sd * (0.2 * d + 0.3 * e + 1.5 * g)

    sorted_x = sorted(tf_idf_sntnc.items(), key=operator.itemgetter(1), reverse=True)
    selected_sentences = []
    current_word_count = 0
    sentences_added = 0

    for sentence, score in sorted_x:
        sentence_word_count = len(word_tokenize(sentence))
        if (current_word_count + sentence_word_count) > word_limit:
            continue
        if sentences_added >= sentence_limit:
            break
        selected_sentences.append((sentence, score))
        current_word_count += sentence_word_count
        sentences_added += 1

    sentence_order = {sentence: idx for idx, sentence in enumerate(sntncs)}
    selected_sentences.sort(key=lambda x: sentence_order.get(x[0], 0))
    summary = " ".join([sentence for sentence, score in selected_sentences])
    return summary


def summarize_text(input_text, dict_path="dictionary.txt", word_limit=600, sentence_limit=40):
    read_legal_dict(dict_path)
    cal_df(input_text)
    summary = cal_tf_Idf(input_text, dict_path, word_limit, sentence_limit)
    return summary
