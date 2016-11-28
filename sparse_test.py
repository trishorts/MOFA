"""
Script to test the spike and slab updates with gaussian and non-gaussian likelihoods
"""

from __future__ import division
from time import time
import cPickle as pkl
import scipy as s
import os
import scipy.special as special
import scipy.stats as stats
import numpy.linalg  as linalg
import pandas as pd

# Import manually defined functions
from simulate import Simulate
from BayesNet import BayesNet
from multiview_nodes import *
from seeger_nodes import Binomial_PseudoY_Node, Poisson_PseudoY_Node, Bernoulli_PseudoY_Node
from local_nodes import Local_Node, Observed_Local_Node
from sparse_updates import Y_Node, Alpha_Node, SW_Node, Tau_Node, Z_Node
from utils import *

###################
## Generate data ##
###################

# Define dimensionalities
M = 3
N = 100
D = s.asarray([100,100,100])
K = 6


## Simulate data  ##
data = {}
tmp = Simulate(M=M, N=N, D=D, K=K)

data['Z'] = s.zeros((N,K))
data['Z'][:,0] = s.sin(s.arange(1,N+1)/(N/20))
data['Z'][:,1] = s.cos(s.arange(N)/(N/20))
data['Z'][:,2] = 2*(s.arange(N)/N-0.5)
data['Z'][:,3] = stats.norm.rvs(loc=0, scale=1, size=N)
data['Z'][:,4] = stats.norm.rvs(loc=0, scale=1, size=N)
data['Z'][:,5] = stats.norm.rvs(loc=0, scale=1, size=N)

# Add a known covariate
# data['Z'] = s.c_[ data['Z'], s.asarray([True,False]*(N/2), dtype=s.float32) ]
# covariate = 6

data['alpha'] = [ s.zeros(K,) for m in xrange(M) ]
data['alpha'][0] = [1,1,1e6,1,1e6,1e6]
data['alpha'][1] = [1,1e6,1,1e6,1,1e6]
data['alpha'][2] = [1e6,1,1,1e6,1e6,1]

theta = [ s.ones(K)*0.5 for m in xrange(M) ]
data['S'], data['W'], data['W_hat'], _ = tmp.initW_spikeslab(theta=theta, alpha=data['alpha'])

data['mu'] = [ s.zeros(D[m]) for m in xrange(M)]
<<<<<<< HEAD
data['tau']= [ stats.uniform.rvs(loc=1,scale=5,size=D[m]) for m in xrange(M) ]
Y_gaussian = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'],
	likelihood="gaussian", missingness=0.05)
# Y_poisson = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], likelihood="poisson")
# Y_bernoulli = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], likelihood="bernoulli")
# Y_binomial = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], likelihood="binomial", min_trials=10, max_trials=50)
=======
>>>>>>> 335e5cb0973af5abdd348daaef33abf5bb9c24cc

data['tau']= [ stats.uniform.rvs(loc=1,scale=3,size=D[m]) for m in xrange(M) ]

Y_gaussian = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], 
	likelihood="gaussian", missingness=0.00)
Y_poisson = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], 
	likelihood="poisson", missingness=0.00)
Y_bernoulli = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], 
	likelihood="bernoulli", missingness=0.00)
# Y_binomial = tmp.generateData(W=data['W'], Z=data['Z'], Tau=data['tau'], Mu=data['mu'], 
	# likelihood="binomial", min_trials=10, max_trials=50, missingness=0.05)

data["Y"] = ( Y_gaussian[0], Y_poisson[1], Y_bernoulli[2] )
# data["Y"] = Y_bernoulli
# data["Y"] = Y_poisson
# data["Y"] = Y_binomial
# data["Y"] = Y_gaussian

# likelihood = ["gaussian","gaussian","gaussian"]
# view_names = ["gaussian1","gaussian2","gaussian3"]
likelihood = ["gaussian","poisson","bernoulli"]
view_names = likelihood

#################################
## Initialise Bayesian Network ##
#################################

net = BayesNet()

# Define initial number of latent variables
K = 10

# Define model dimensionalities
net.dim["M"] = M
net.dim["N"] = N
net.dim["D"] = D
net.dim["K"] = K

###############
## Add nodes ##
###############

# Z without covariates (variational node)
Z_pmean = 0.
Z_pvar = 1.
Z_qmean = s.stats.norm.rvs(loc=0, scale=1, size=(N,K))
Z_qvar = s.ones((N,K))
Z = Z_Node(dim=(N,K), pmean=Z_pmean, pvar=Z_pvar, qmean=Z_qmean, qvar=Z_qvar)

# Z with covariates (variational node)
# Z_pmean = 0.
# Z_pvar = 1.
# Z_qmean = s.stats.norm.rvs(loc=0, scale=1, size=(N,K-1))
# Z_qmean = s.c_[ Z_qmean, s.asarray([True,False]*(N/2), dtype=s.float32) ]
# Z_qvar = s.ones((N,K))
# Z = Z_Node(dim=(N,K), pmean=Z_pmean, pvar=Z_pvar, qmean=Z_qmean, qvar=Z_qvar)
# Z.setCovariates(idx=K-1)

# alpha (variational node)
alpha_list = [None]*M
alpha_pa = 1e-14
alpha_pb = 1e-14
alpha_qb = s.ones(K)
alpha_qa = s.ones(K)
alpha_qE = s.ones(K)*100
for m in xrange(M):
	alpha_list[m] = Alpha_Node(dim=(K,), pa=alpha_pa, pb=alpha_pb, qa=alpha_qa, qb=alpha_qb, qE=alpha_qE)
	alpha_qa = alpha_pa + s.ones(K)*D[m]/2
	# alpha_list[m] = Alpha_Node(dim=(K,), pa=alpha_pa, pb=alpha_pb, qa=alpha_qa[m], qb=alpha_qb, qE=alpha_qE)
alpha = Multiview_Variational_Node((K,)*M, *alpha_list)


# W (variational node)
SW_list = [None]*M
S_ptheta = 0.5
for m in xrange(M):
	S_qtheta = s.ones((D[m],K))*S_ptheta
	W_qmean = s.stats.norm.rvs(loc=0, scale=1, size=(D[m],K))
	W_qvar = s.ones((D[m],K))
	SW_list[m] = SW_Node(dim=(D[m],K), ptheta=S_ptheta, qtheta=S_qtheta, qmean=W_qmean, qvar=W_qvar)
SW = Multiview_Variational_Node(M, *SW_list)


# tau/kappa (mixed node)
tau_list = [None]*M
for m in xrange(M):
<<<<<<< HEAD
	if m in M_poisson:
		tmp = 0.25 + 0.17*s.amax(data["Y"][m],axis=0)
		tau_list[m] = Observed_Local_Node(dim=(D[m],), value=tmp)
	elif m in M_bernoulli:
		tmp = s.ones(D[m])*0.25
=======
	if likelihood[m] == "poisson":
		tmp = 0.25 + 0.17*s.amax(data["Y"][m],axis=0) 
		tau_list[m] = Observed_Local_Node(dim=(D[m],), value=tmp)
	elif likelihood[m] == "bernoulli":
		tmp = s.ones(D[m])*0.25 
>>>>>>> 335e5cb0973af5abdd348daaef33abf5bb9c24cc
		tau_list[m] = Observed_Local_Node(dim=(D[m],), value=tmp)
	elif likelihood[m] == "binomial":
		tmp = 0.25*s.amax(data["Y"]["tot"][m],axis=0)
		tau_list[m] = Observed_Local_Node(dim=(D[m],), value=tmp)
	elif likelihood[m] == "gaussian":
		tau_pa = 1e-14
		tau_pb = 1e-14
		tau_qa = tau_pa + s.ones(D[m])*N/2
		tau_qb = s.zeros(D[m])
		tau_qE = s.zeros(D[m]) + 100
		tau_list[m] = Tau_Node(dim=(D[m],), pa=tau_pa, pb=tau_pb, qa=tau_qa, qb=tau_qb, qE=tau_qE)
tau = Multiview_Mixed_Node(M,*tau_list)


<<<<<<< HEAD
# zeta (local node)
# not initialised since it is the first update
Zeta_list = [None]*M
for m in xrange(M):
	if m not in M_gaussian:
		Zeta_list[m] = Zeta_Node(dim=(N,D[m]), initial_value=None)
	else:
		Zeta_list[m] = None
Zeta = Multiview_Local_Node(M, *Zeta_list)


=======
>>>>>>> 335e5cb0973af5abdd348daaef33abf5bb9c24cc
# Y/Yhat (mixed node)
Y_list = [None]*M
for m in xrange(M):
	if likelihood[m] == "gaussian":
		Y_list[m] = Y_Node(dim=(N,D[m]), obs=data['Y'][m])
	elif likelihood[m] == "poisson":
		Y_list[m] = Poisson_PseudoY_Node(dim=(N,D[m]), obs=data['Y'][m], Zeta=None, E=None)
	elif likelihood[m] == "bernoulli":
		Y_list[m] = Bernoulli_PseudoY_Node(dim=(N,D[m]), obs=data['Y'][m], Zeta=None, E=None)
	elif likelihood[m] == "binomial":
		Y_list[m] = Binomial_PseudoY_Node(dim=(N,D[m]), tot=data['Y']["tot"][m], obs=data['Y']["obs"][m], Zeta=None, E=None)
Y = Multiview_Mixed_Node(M, *Y_list)

############################
## Define Markov Blankets ##
############################

Z.addMarkovBlanket(SW=SW, tau=tau, Y=Y)
for m in xrange(M):
	alpha.nodes[m].addMarkovBlanket(SW=SW.nodes[m])
	SW.nodes[m].addMarkovBlanket(Z=Z, tau=tau.nodes[m], alpha=alpha.nodes[m], Y=Y.nodes[m])
	if likelihood[m] == "gaussian":
		Y.nodes[m].addMarkovBlanket(Z=Z, SW=SW.nodes[m], tau=tau.nodes[m])
		tau.nodes[m].addMarkovBlanket(SW=SW.nodes[m], Z=Z, Y=Y.nodes[m])
	else:
		Y.nodes[m].addMarkovBlanket(Z=Z, W=SW.nodes[m], kappa=tau.nodes[m])

##################################
## Update required expectations ##
##################################

SW.updateExpectations()
Z.Q.updateExpectations()

##################################
## Add the nodes to the network ##
##################################

net.addNodes(SW=SW, tau=tau, Z=Z, Y=Y, alpha=alpha)

# Define update schedule
schedule = ["Y","SW","Z","alpha","tau"]

net.setSchedule(schedule)

#############################
## Define training options ##
#############################

options = {}
options['maxiter'] = 200
options['tolerance'] = 1E-2
options['forceiter'] = True
# options['elbofreq'] = options['maxiter']+1
options['elbofreq'] = 1
options['dropK'] = True
options['dropK_threshold'] = 0.03
options['savefreq'] = options['maxiter']+1
options['savefolder'] = "/tmp/test"
options['verbosity'] = 2
net.options = options


####################
## Start training ##
####################

net.iterate()

##################
## Save results ##
##################

<<<<<<< HEAD

outdir="/tmp/test"

if not os.path.exists(outdir):
    os.makedirs(outdir)
if not os.path.exists(os.path.join(outdir,"data")):
    os.makedirs(os.path.join(outdir,"data"))
if not os.path.exists(os.path.join(outdir,"model")):
    os.makedirs(os.path.join(outdir,"model"))
if not os.path.exists(os.path.join(outdir,"stats")):
    os.makedirs(os.path.join(outdir,"stats"))
if not os.path.exists(os.path.join(outdir,"opts")):
    os.makedirs(os.path.join(outdir,"opts"))

# Save the model parameters and expectations
print "\nSaving model..."
saveModel(net, outdir=os.path.join(outdir,"model"), only_first_moments=True)

# Save training statistics
print "\nSaving training stats..."
opts = saveTrainingStats(model=net, outdir=os.path.join(outdir,"stats"))

# Save training options
print "\nSaving training opts..."
opts = saveTrainingOpts(model=net, outdir=os.path.join(outdir,"opts"))
=======
print "\nSaving model..."
sample_names = [ "sample_%d" % n for n in xrange(N)]
feature_names = [[ "feature_%d" % n for n in xrange(D[m])] for m in xrange(M)]

saveModel(net, outfile="/tmp/test/asd.hd5", view_names=view_names, 
	sample_names=sample_names, feature_names=feature_names)
>>>>>>> 335e5cb0973af5abdd348daaef33abf5bb9c24cc