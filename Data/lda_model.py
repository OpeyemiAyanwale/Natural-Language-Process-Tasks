from __future__ import print_function
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.datasets import fetch_20newsgroups
import numpy as np
import logging
import lda._lda
import lda.utils

logger = logging.getLogger(__name__)

class LDA_Model:
	def __init__(self, documents=None,max_df=.50,min_df=2):
		self.documents = documents
		self.max_df = max_df
		self.min_df = min_df
		if len(logger.handlers) == 1 and isinstance(logger.handlers[0], logging.NullHandler):
			logging.basicConfig(level=logging.DEBUG)
	def set_documents(self,documents):
		self.documents = documents

	def documents_to_topic_model(self,n_topics,n_features,n_iter,seed_words=None,original=False,m=10):
		print("Extracting tf features for LDA...")
		# We use a few heuristics to filter out useless terms early on: the posts are stripped of headers,
		# footers and quoted replies, and common English words, words occurring in only one document or 
		# in at least 95% of the documents are removed. Use tf (raw term count) features for LDA.
		# tf is a csr_matrix 
		tf_vectorizer = CountVectorizer(max_df=self.max_df, min_df=self.min_df, max_features=n_features)
		tf = tf_vectorizer.fit_transform(self.documents)
		self.vocab = tf_vectorizer.get_feature_names()
		tf2 = self.remove_zero_rows(tf)
		self.X = X = tf2.toarray()
		
		# TODO: currently crashes if a seed_word is not in the vocab
		seeds = self.get_seed_indices(seed_words)

		self.model = LDA(n_topics=n_topics, n_iter=n_iter, random_state=1,refresh=100)
		if original:
			self.model.fit(X)
		else:
			self.model.fit_seeded(X,seeds,m)

	def test(self,n):
		return self.model.transform(self.X[n])


	def remove_zero_rows(self,X):
	    # X is a scipy sparse matrix. We want to remove all zero rows from it
	    nonzero_row_indice, _ = X.nonzero()
	    unique_nonzero_indice = np.unique(nonzero_row_indice)
	    logger.info("Removed {} all zero rows".format(X.shape[0]-X[unique_nonzero_indice].shape[0]))
	    return X[unique_nonzero_indice]

	def get_seed_indices(self,seed_words):
		if seed_words == None:
			return None
		seeds = []
		for i,topic in enumerate(seed_words):
			s = []
			for j,seed in enumerate(topic):
				if seed in self.vocab:
					s.append(self.vocab.index(seed))
				else:
					logger.info("The seed word '{}' wasn't in the vocabulary".format(seed))
			seeds.append(s)
		return seeds

	def display_topics(self, n_top_words):
	    topic_word = self.model.topic_word_
	    for i, topic_dist in enumerate(topic_word):
	    	topic_words = np.array(self.vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
	    	print('Topic {}: {}'.format(i, ' '.join(topic_words)))
	    	indices = np.argsort(topic_dist)
	    	# logger.debug(indices)
	    	logger.debug(topic_dist[indices[len(indices)-n_top_words]])

	def get_top_words(self,p=.002):
		topic_word = self.model.topic_word_
		top_words = []
		for i,topic_dist in enumerate(topic_word):
			indices = np.argsort(topic_dist)[::-1]
			I = len(indices)
			for j in range(1,len(indices)):
				if topic_dist[indices[j]] < p:
					I = j
					logger.debug('Topic {} has {} words with p>{}'.format(i,I,p))
					break
			temp = np.array(self.vocab)[indices[:I]]
			# print('Topic {}: {}'.format(i,' '.join(temp)))
			top_words.append(temp)
		return top_words

	def get_top_words_absolute(self,n=100):
		topic_word = self.model.topic_word_
		top_words = []
		for i,topic_dist in enumerate(topic_word):
			topic_words = np.array(self.vocab)[np.argsort(topic_dist)][:-n+1:-1]
			top_words.append(topic_words)
		return top_words
class LDA:
	"""Latent Dirichlet allocation using collapsed Gibbs sampling

    Parameters
    ----------
    n_topics : int
        Number of topics

    n_iter : int, default 2000
        Number of sampling iterations

    alpha : float, default 0.1
        Dirichlet parameter for distribution over topics

    eta : float, default 0.01
        Dirichlet parameter for distribution over words

    random_state : int or RandomState, optional
        The generator used for the initial topics.

    Attributes
    ----------
    `components_` : array, shape = [n_topics, n_features]
        Point estimate of the topic-word distributions (Phi in literature)
    `topic_word_` :
        Alias for `components_`
    `nzw_` : array, shape = [n_topics, n_features]
        Matrix of counts recording topic-word assignments in final iteration.
    `ndz_` : array, shape = [n_samples, n_topics]
        Matrix of counts recording document-topic assignments in final iteration.
    `doc_topic_` : array, shape = [n_samples, n_features]
        Point estimate of the document-topic distributions (Theta in literature)
    `nz_` : array, shape = [n_topics]
        Array of topic assignment counts in final iteration.

    Examples
    --------
    >>> import numpy
    >>> X = numpy.array([[1,1], [2, 1], [3, 1], [4, 1], [5, 8], [6, 1]])
    >>> import lda
    >>> model = lda.LDA(n_topics=2, random_state=0, n_iter=100)
    >>> model.fit(X) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    LDA(alpha=...
    >>> model.components_
    array([[ 0.85714286,  0.14285714],
           [ 0.45      ,  0.55      ]])
    >>> model.loglikelihood() #doctest: +ELLIPSIS
    -40.395...

    References
    ----------
    Blei, David M., Andrew Y. Ng, and Michael I. Jordan. "Latent Dirichlet
    Allocation." Journal of Machine Learning Research 3 (2003): 993–1022.

    Griffiths, Thomas L., and Mark Steyvers. "Finding Scientific Topics."
    Proceedings of the National Academy of Sciences 101 (2004): 5228–5235.
    doi:10.1073/pnas.0307752101.

    Wallach, Hanna, David Mimno, and Andrew McCallum. "Rethinking LDA: Why
    Priors Matter." In Advances in Neural Information Processing Systems 22,
    edited by Y.  Bengio, D. Schuurmans, J. Lafferty, C. K. I. Williams, and A.
    Culotta, 1973–1981, 2009.

    Buntine, Wray. "Estimating Likelihoods for Topic Models." In Advances in
    Machine Learning, First Asian Conference on Machine Learning (2009): 51–64.
    doi:10.1007/978-3-642-05224-8_6.

    """

	def __init__(self, n_topics, n_iter=2000, alpha=0.1, eta=0.01, random_state=None,
				 refresh=10):
		self.n_topics = n_topics
		self.n_iter = n_iter
		self.alpha = alpha
		self.eta = eta
		# if random_state is None, check_random_state(None) does nothing
		# other than return the current numpy RandomState
		self.random_state = random_state
		self.refresh = refresh

		if alpha <= 0 or eta <= 0:
			raise ValueError("alpha and eta must be greater than zero")

		# random numbers that are reused
		rng = lda.utils.check_random_state(random_state)
		self._rands = rng.rand(1024 ** 2 // 8)  # 1MiB of random variates

		# configure console logging if not already configured
		if len(logger.handlers) == 1 and isinstance(logger.handlers[0], logging.NullHandler):
			logging.basicConfig(level=logging.INFO)

	def fit(self, X, y=None):
		"""Fit the model with X.

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training data, where n_samples in the number of samples
            and n_features is the number of features. Sparse matrix allowed.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
		self._fit(X)
		return self

	def fit_seeded(self, X, seeds=None, m=10):
		"""Fit the model with X.

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training data, where n_samples in the number of samples
            and n_features is the number of features. Sparse matrix allowed.

        seeds: list of lists. each inner list should be a list of indices that refer
        to words in the vocab of X
        Returns
        -------
        self : object
            Returns the instance itself.
        """
		self._fit_seeded(X, seeds, m)
		return self

	def fit_transform(self, X, y=None):
		"""Apply dimensionality reduction on X

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            New data, where n_samples in the number of samples
            and n_features is the number of features. Sparse matrix allowed.

        Returns
        -------
        doc_topic : array-like, shape (n_samples, n_topics)
            Point estimate of the document-topic distributions

        """
		if isinstance(X, np.ndarray):
			# in case user passes a (non-sparse) array of shape (n_features,)
			# turn it into an array of shape (1, n_features)
			X = np.atleast_2d(X)
		self._fit(X)
		return self.doc_topic_

	def transform(self, X, max_iter=20, tol=1e-16):
		"""Transform the data X according to previously fitted model

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            New data, where n_samples in the number of samples
            and n_features is the number of features.
        max_iter : int, optional
            Maximum number of iterations in iterated-pseudocount estimation.
        tol: double, optional
            Tolerance value used in stopping condition.

        Returns
        -------
        doc_topic : array-like, shape (n_samples, n_topics)
            Point estimate of the document-topic distributions

        Note
        ----
        This uses the "iterated pseudo-counts" approach described
        in Wallach et al. (2009) and discussed in Buntine (2009).

        """
		if isinstance(X, np.ndarray):
			# in case user passes a (non-sparse) array of shape (n_features,)
			# turn it into an array of shape (1, n_features)
			X = np.atleast_2d(X)
		doc_topic = np.empty((X.shape[0], self.n_topics))
		WS, DS = lda.utils.matrix_to_lists(X)
		# TODO: this loop is parallelizable
		for d in np.unique(DS):
			doc_topic[d] = self._transform_single(WS[DS == d], max_iter, tol)
		return doc_topic

	def _transform_single(self, doc, max_iter, tol):
		"""Transform a single document according to the previously fit model

        Parameters
        ----------
        X : 1D numpy array of integers
            Each element represents a word in the document
        max_iter : int
            Maximum number of iterations in iterated-pseudocount estimation.
        tol: double
            Tolerance value used in stopping condition.

        Returns
        -------
        doc_topic : 1D numpy array of length n_topics
            Point estimate of the topic distributions for document

        Note
        ----

        See Note in `transform` documentation.

        """
		PZS = np.zeros((len(doc), self.n_topics))
		for iteration in range(max_iter + 1):  # +1 is for initialization
			PZS_new = self.components_[:, doc].T
			PZS_new *= (PZS.sum(axis=0) - PZS + self.alpha)
			PZS_new /= PZS_new.sum(axis=1)[:, np.newaxis]  # vector to single column matrix
			delta_naive = np.abs(PZS_new - PZS).sum()
			logger.debug('transform iter {}, delta {}'.format(iteration, delta_naive))
			PZS = PZS_new
			if delta_naive < tol:
				break
		theta_doc = PZS.sum(axis=0) / PZS.sum()
		assert len(theta_doc) == self.n_topics
		assert theta_doc.shape == (self.n_topics,)
		return theta_doc

	def _fit(self, X):
		"""Fit the model to the data X

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training vector, where n_samples in the number of samples and
            n_features is the number of features. Sparse matrix allowed.
        """
		# if self.random_state is an integer, a RandomState(seed) object is returned
		# if its a RandomState object it is returned
		random_state = lda.utils.check_random_state(self.random_state)

		# rands is an array of 131072 random numbers
		rands = self._rands.copy()
		self._initialize(X)
		for it in range(self.n_iter):
			# FIXME: using numpy.roll with a random shift might be faster
			# shuffle the random numbers in rand in place
			random_state.shuffle(rands)
			if it % self.refresh == 0:
				ll = self.loglikelihood()
				logger.info("<{}> log likelihood: {:.0f}".format(it, ll))
				# keep track of loglikelihoods for monitoring convergence
				self.loglikelihoods_.append(ll)
			self._sample_topics(rands)
		ll = self.loglikelihood()
		logger.info("<{}> log likelihood: {:.0f}".format(self.n_iter - 1, ll))
		# note: numpy /= is integer division
		self.components_ = (self.nzw_ + self.eta).astype(float)
		self.components_ /= np.sum(self.components_, axis=1)[:, np.newaxis]
		self.topic_word_ = self.components_
		self.doc_topic_ = (self.ndz_ + self.alpha).astype(float)
		self.doc_topic_ /= np.sum(self.doc_topic_, axis=1)[:, np.newaxis]

		# delete attributes no longer needed after fitting to save memory and reduce clutter
		del self.WS
		del self.DS
		del self.ZS
		return self

	def _fit_seeded(self, X, seeds=None, m=10):
		"""Fit the model to the data X

        Parameters
        ----------
        X: array-like, shape (n_samples, n_features)
            Training vector, where n_samples in the number of samples and
            n_features is the number of features. Sparse matrix allowed.
        """
		# if self.random_state is an integer, a RandomState(seed) object is returned
		# if its a RandomState object it is returned
		random_state = lda.utils.check_random_state(self.random_state)

		# rands is an array of 131072 random numbers
		rands = self._rands.copy()
		self._seeds = seeds
		if seeds == None:
			self._initialize(X)
		else:
			self._initialize_seeded(X, m)
		for it in range(self.n_iter):
			# FIXME: using numpy.roll with a random shift might be faster
			# shuffle the random numbers in rand in place
			random_state.shuffle(rands)
			if it % self.refresh == 0:
				ll = self.loglikelihood()
				logger.info("<{}> log likelihood: {:.0f}".format(it, ll))
				# keep track of loglikelihoods for monitoring convergence
				self.loglikelihoods_.append(ll)
			self._sample_topics(rands)
		ll = self.loglikelihood()
		logger.info("<{}> log likelihood: {:.0f}".format(self.n_iter - 1, ll))
		# note: numpy /= is integer division
		self.components_ = (self.nzw_ + self.eta).astype(float)
		self.components_ /= np.sum(self.components_, axis=1)[:, np.newaxis]
		self.topic_word_ = self.components_
		self.doc_topic_ = (self.ndz_ + self.alpha).astype(float)
		self.doc_topic_ /= np.sum(self.doc_topic_, axis=1)[:, np.newaxis]

		# delete attributes no longer needed after fitting to save memory and reduce clutter
		del self.WS
		del self.DS
		del self.ZS
		return self

	def _initialize(self, X):
		# X is the doc-term matrix. documents x features (vocab size)
		D, W = X.shape
		N = int(X.sum())
		n_topics = self.n_topics
		n_iter = self.n_iter
		logger.info("n_documents: {}".format(D))
		logger.info("vocab_size: {}".format(W))
		logger.info("n_words: {}".format(N))
		logger.info("n_topics: {}".format(n_topics))
		logger.info("n_iter: {}".format(n_iter))

		self.nzw_ = nzw_ = np.zeros((n_topics, W), dtype=np.intc)
		self.ndz_ = ndz_ = np.zeros((D, n_topics), dtype=np.intc)
		self.nz_ = nz_ = np.zeros(n_topics, dtype=np.intc)

		self.WS, self.DS = WS, DS = lda.utils.matrix_to_lists(X)
		self.ZS = ZS = np.empty_like(self.WS, dtype=np.intc)
		np.testing.assert_equal(N, len(WS))
		for i in range(N):
			w, d = WS[i], DS[i]
			z_new = i % n_topics
			ZS[i] = z_new
			ndz_[d, z_new] += 1
			nzw_[z_new, w] += 1
			nz_[z_new] += 1
		self.loglikelihoods_ = []

	def _initialize_seeded(self, X, m=10):
		# X is the doc-term matrix. documents x features (vocab size)
		D, W = X.shape
		N = int(X.sum())
		n_topics = self.n_topics
		n_iter = self.n_iter
		logger.info("n_documents: {}".format(D))
		logger.info("vocab_size: {}".format(W))
		logger.info("n_words: {}".format(N))
		logger.info("n_topics: {}".format(n_topics))
		logger.info("n_iter: {}".format(n_iter))

		self.nzw_ = nzw_ = np.zeros((n_topics, W), dtype=np.intc)
		self.ndz_ = ndz_ = np.zeros((D, n_topics), dtype=np.intc)
		self.nz_ = nz_ = np.zeros(n_topics, dtype=np.intc)

		# WS is an array of all the words in the documents
		# DS contains which document each words belongs to
		self.WS, self.DS = WS, DS = lda.utils.matrix_to_lists(X)
		# ZS is an array of length N. it contains what topic each word is initially assigned to
		self.ZS = ZS = np.empty_like(self.WS, dtype=np.intc)
		np.testing.assert_equal(N, len(WS))
		# seeds = [[657,370,900,277],[831,597,282,493]]
		# m = N//100
		# m=10
		for i in range(N):
			w, d = WS[i], DS[i]
			is_seed = 0
			for n in range(len(self._seeds)):
				if w in self._seeds[n]:
					z_new = n
					is_seed = 1

			if is_seed:
				# logger.info("found seed: {}".format(w))
				ZS[i] = z_new
				ndz_[d, z_new] += m
				nzw_[z_new, w] += m
				nz_[z_new] += m
			else:
				z_new = i % n_topics
				ZS[i] = z_new
				ndz_[d, z_new] += 1
				nzw_[z_new, w] += 1
				nz_[z_new] += 1
		self.loglikelihoods_ = []

	def loglikelihood(self):
		"""Calculate complete log likelihood, log p(w,z)

        Formula used is log p(w,z) = log p(w|z) + log p(z)
        """
		nzw, ndz, nz = self.nzw_, self.ndz_, self.nz_
		alpha = self.alpha
		eta = self.eta
		nd = np.sum(ndz, axis=1).astype(np.intc)
		return lda._lda._loglikelihood(nzw, ndz, nz, nd, alpha, eta)

	def _sample_topics(self, rands):
		"""Samples all topic assignments. Called once per iteration."""
		n_topics, vocab_size = self.nzw_.shape
		alpha = np.repeat(self.alpha, n_topics).astype(np.float64)
		eta = np.repeat(self.eta, vocab_size).astype(np.float64)
		lda._lda._sample_topics(self.WS, self.DS, self.ZS, self.nzw_, self.ndz_, self.nz_,
								alpha, eta, rands)

	def log_perplexity(self, X):
		""" formula:
        https://shuyo.wordpress.com/2011/05/24/collapsed-gibbs-sampling-estimation-for-latent-dirichlet-allocation-1/#comment-706

        """
		# n_features = self.components_.shape[1]
		# n_topics = self.doc_topic_.shape[1]
		# Phi = (self.nzw_ + self.eta).astype(float) / (self.n_topics + n_features * self.eta)
		# Theta_temp = np.divide(1, self.ndz_.sum(axis=1) + n_topics * self.alpha)
		# Theta_temp2 = (self.ndz_ + self.alpha).astype(float)
		# Theta = Theta_temp2 * Theta_temp[:, np.newaxis]

		# dwmatrix = np.log(np.dot(Theta,Phi))  # shape: [n_samples, n_features]= [m,n](in the website above)
		# log_perp = dwmatrix.sum() / self.nzw_.sum()
		# return log_perp

		n_features = self.components_.shape[1]
		n_topics = self.doc_topic_.shape[1]
		Phi = (self.nzw_ + self.eta).astype(float) / (self.n_topics + n_features * self.eta)
		Theta_temp = np.divide(1, self.ndz_.sum(axis=1) + n_topics * self.alpha)
		Theta_temp2 = (self.ndz_ + self.alpha).astype(float)
		Theta = Theta_temp2 * Theta_temp[:, np.newaxis]  # *：点乘

		dwmatrix = np.log(np.dot(Theta, Phi))  # shape: [n_samples, n_features]= [m,n](in the website above)
		dwmatrix = X * dwmatrix  # multiply by element
		log_perp = dwmatrix.sum() / self.nzw_.sum()
		return np.exp(log_perp)

	def perplexity(self):
		""" formula:
        https://shuyo.wordpress.com/2011/05/24/collapsed-gibbs-sampling-estimation-for-latent-dirichlet-allocation-1/#comment-706

        """
		n_features = self.components_.shape[1]
		n_topics = self.doc_topic_.shape[1]
		Phi = (self.nzw_ + self.eta).astype(float) / (self.n_topics + n_features * self.eta)
		Theta_temp = np.divide(1, self.ndz_.sum(axis=1) + n_topics * self.alpha)
		Theta_temp2 = (self.ndz_ + self.alpha).astype(float)
		Theta = Theta_temp2 * Theta_temp[:, np.newaxis]  # *：点乘

		dwmatrix = np.log(Theta * Phi)  # shape: [n_samples, n_features]= [m,n](in the website above)
		dwmatrix = self.X_ * dwmatrix  # multiply by element
		log_perp = dwmatrix.sum() / self.nzw_.sum()
		return np.exp(-log_perp)

