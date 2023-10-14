import random
import pandas
import numpy
import numpy.matlib
import scipy
import torch
import sys

def main():
    random.seed(2019)
    torch.set_printoptions(precision=5)
    numpy.set_printoptions(suppress=True)
    pandas.set_option('expand_frame_repr', True)
    numpy.set_printoptions(threshold=sys.maxsize)
    #Load data set
    dataFile = "Data_Set.csv"
    dataFrame = pandas.read_csv(dataFile, header=None)
    GenoType = numpy.array(dataFrame[1].tolist())
    GenoType_Names = ["FoxP2 Knock-Down","Wild Type"]
    Context = numpy.array(dataFrame[2].tolist())
    Context_Names = ["U","L","A"]
    MouseId = numpy.array(dataFrame[0].tolist())
    Ytminus1 = numpy.array(dataFrame[3].tolist())
    Yt = numpy.array(dataFrame[4].tolist())
    Ytminus1_Orgnl = Ytminus1
    Yt_Orgnl = Yt
    d0 = numpy.unique(Yt).size
    Xexgns = numpy.column_stack([GenoType, Context])
    sz = Xexgns.shape
    p = sz[1]
    dpreds = numpy.zeros((p,), dtype=int)
    #Number of levels in each exegenous predictors
    for j in range(0,p):
        dpreds[j] = numpy.unique(Xexgns[:,j]).size
    #Find sequence lengths
    v0 = numpy.column_stack([Xexgns,MouseId])
    v0 = numpy.sort(v0, axis=-1)
    #Sorted unique combinations
    v00, m00 = numpy.unique(v0,return_index=True,axis=0)
    Ts = numpy.diff(numpy.append(m00,v0.shape[0]))
    m00m00starts = m00
    sequencesStats = numpy.column_stack([v00,Ts])

    #Assign priors
    pialpha = numpy.ones((p,), dtype=int)
    dmax = numpy.amax(dpreds)
    lambdaalpha_exgns = 1
    lambdaalpha_anmls = 1
    lambdaalpha0 = 1

    #MCMC sampler
    #Number of MCMC iterations
    N_MCMC = 10
    #Number of iterations for which the results are stored
    N_Store = 0
    #Thining interval
    N_Thin = 1
    #Number of predictors included in the model
    np = p
    Xnew = Xexgns
    M = numpy.matlib.repmat(dpreds,N_MCMC+1,1)
    G = numpy.zeros((p,dmax), dtype=int)
    pi = numpy.zeros((p,dmax), dtype=float)
    logmarginalsprobs = numpy.zeros((p,dmax), dtype=int)
    sz = Xnew.shape
    Ntot = sz[0]

    z = numpy.ones((Ntot,p), dtype=int)

    for j in range(0,p):
        indices = numpy.arange(0,dpreds[j])
        for i in indices:
            G[j][i] = i + 1
        for i in range(0,Ntot):
            z[i][j] = Xnew[i][j]
        prob = float(1/dpreds[j])
        for i in indices:
            pi[j][i] = prob

    GG = G
    log0 = numpy.zeros((N_MCMC,1), dtype=int)
    #All mice, first column genotype, second column id
    miceallStackedArray = numpy.column_stack([Xnew[:,0],MouseId])
    miceallStackedArray = numpy.sort(miceallStackedArray, axis=-1)
    miceall = numpy.unique(miceallStackedArray,return_index=True,axis=0)
    miceall = miceall[0]
    #(1-piv) are probs of following the main effects
    piv = 0.8*numpy.ones((1,d0), dtype=float)
    piv = piv[0]
    v = numpy.random.choice(numpy.array([0,1]),Ntot,True,numpy.array([(piv[0]),(1-piv[0])]))

    #Estimating all transition probabilities TP_All step 1
    #d0=levels of y_{s,t}, d0=levels of y_{s,t-1}, dpreds levels of exogenous predictors
    dimensionList = []
    dimensionList.extend([numpy.max(MouseId)])
    dimensionList.extend(reversed(dpreds))
    dimensionList.extend([d0, d0])
    C = torch.zeros(dimensionList, dtype=torch.int32)

    #Find sequence lengths and update tensor C
    v0 = pandas.DataFrame(numpy.column_stack([Yt,Ytminus1,Xnew,MouseId])).sort_values(by=[0,1],axis=0)
    v00, m00 = numpy.unique(v0[[0,1,2,3,4]],return_index=True,axis=0)
    m00 = numpy.append(m00, v0.shape[0])
    v00_tensor = torch.Tensor(v00.tolist())
    v00_tensor = v00_tensor.type(torch.LongTensor)
    m00_diff_tensor = torch.from_numpy(numpy.diff(m00)).unsqueeze(0).t()
    i = 0
    for tensor_value in v00_tensor:
        C[int(tensor_value[4]) - 1][int(tensor_value[3]) - 1][int(tensor_value[2]) - 1][int(tensor_value[0]) - 1][int(tensor_value[1]) - 1] = m00_diff_tensor[i]
        i = i + 1

    # Estimate TP_All step 2a
    T_All = C.type(torch.double)
    TP_All = torch.zeros(dimensionList, dtype=torch.double)
    T_All_Sum = T_All.sum(3)
    T_All_Sum_Expanded = T_All_Sum.expand(8,3,2,5).repeat(1,1,1,5).view(8,3,2,5,5)
    TP_All = torch.div(T_All,T_All_Sum_Expanded)
    TP_All[TP_All != TP_All] = 0
    T_All = T_All.int()

    #Estimate TP_Anmls step 2b
    T_Anmls = T_All.sum(1).view(8,2,5,5).double()
    TP_Anmls = torch.zeros([8,2,5,5], dtype=torch.double)
    T_Anmls_Sum = T_Anmls.sum(3)
    T_Anmls_Sum_Expanded = T_Anmls_Sum.expand(8,2,5).repeat(1,1,5).view(8,2,5,5).double()
    TP_Anmls = torch.div(T_Anmls, T_Anmls_Sum_Expanded)
    TP_Anmls[TP_Anmls != TP_Anmls] = 0
    T_Anmls = T_Anmls.int()

    #Estimate TP_Exgns step 2c
    T_Exgns = T_All.sum(0).view(3,2,5,5).double()
    TP_Exgns = torch.zeros([3,2,5,5], dtype=torch.double)
    T_Exgns_Sum = T_Exgns.sum(3)
    T_Exgns_Sum_Expanded = T_Exgns_Sum.repeat(1,1,1,5).view(3,2,5,5).double()
    TP_Exgns = torch.div(T_Exgns, T_Exgns_Sum_Expanded)
    TP_Exgns[TP_Exgns != TP_Exgns] = 0
    T_Exgns = T_Exgns.int()

    #Initialize lambda00: step1
    #d0=levels of y_{s,t}, d0=levels of y_{s,t-1}
    C = torch.zeros([5,1], dtype=torch.double)
    #v0 are the sorted unique combinations of (y_{s,t},y_{s,t-1})
    v0 = pandas.DataFrame(numpy.column_stack([Yt])).sort_values(by=[0], axis=0)
    #v00 are the sorted unique combinations of (y_{s,t},y_{s,t-1}), m00 contains their position
    v00, m00 = numpy.unique(v0[0], return_index=True, axis=0)
    m00 = numpy.append(m00, v0.shape[0])
    v00_tensor = torch.Tensor(v00.tolist())
    v00_tensor = v00_tensor.type(torch.LongTensor)
    m00_diff_tensor = torch.from_numpy(numpy.diff(m00)).unsqueeze(0).t()
    i = 0
    for tensor_value in v00_tensor:
        C[int(tensor_value) - 1] = m00_diff_tensor[i]
        i = i + 1
    sz = C.shape
    # initialize lambda00: step2
    a = torch.zeros(d0,sz[1])
    lambda00_mat = torch.zeros(d0,sz[1])
    a = C
    a_sum = a.sum()
    a_sum_expanded = a_sum.repeat(5,1).double()
    lambda00_mat = torch.div(a, a_sum_expanded)
    lambda00 = lambda00_mat
    lambda00_mat_expanded = lambda00_mat.repeat(1,5).double()

    #initialize lambda0: step1
    #d0=levels of y_{s,t}, d0=levels of y_{s,t-1}
    C = torch.zeros([d0, d0], dtype=torch.double)
    #v0 are the sorted unique combinations of (y_{s,t},y_{s,t-1})
    v0 = pandas.DataFrame(numpy.column_stack([Yt, Ytminus1])).sort_values(by=[0,1], axis=0)
    #v00 are the sorted unique combinations of (y_{s,t},y_{s,t-1}), m00 contains their position
    v00, m00 = numpy.unique(v0[[0,1]], return_index=True, axis=0)
    m00 = numpy.append(m00, v0.shape[0])
    v00_tensor = torch.Tensor(v00.tolist())
    v00_tensor = v00_tensor.type(torch.LongTensor)
    m00_diff_tensor = torch.from_numpy(numpy.diff(m00)).unsqueeze(0).t()
    i = 0
    for tensor_value in v00_tensor:
        C[int(tensor_value[0]) - 1][int(tensor_value[1]) - 1] = m00_diff_tensor[i]
        i = i + 1
    sz = C.shape
    #initialize lambda0: step2
    a = torch.zeros(d0, sz[1])
    lambda0_mat = torch.zeros(d0, sz[1])
    a = C
    a_sum = a.sum(0)
    a_sum_expanded = a_sum.repeat(5, 1).double()
    lambda0_mat = torch.div(a, a_sum_expanded)
    lambda0_mat[lambda0_mat == 0] = 0.0001
    lambda0_emp = lambda0_mat
    lambda0 = lambda0_emp
    lambda0_mat_expanded_exgns = lambda0_mat.repeat(1,6)
    lambda0_mat_expanded_anmls = lambda0_mat.repeat(1, 2 * numpy.max(MouseId))

    #initialize lambda_exgns: step1
    #d0=levels of y_{s,t}, d0=levels of y_{s,t-1}, dpreds=number of levels of x_{s,1},...,x_{s,p}
    C = torch.zeros([dpreds[1],dpreds[0],d0, d0], dtype=torch.double)
    #v0 are the sorted unique combinations of (y_{s,t-1},MouseId,z_{s,1},...,z_{s,p})
    v0 = pandas.DataFrame(numpy.column_stack([Yt, Ytminus1, z])).sort_values(by=[0,1,2,3], axis=0)
    #v00 are the sorted unique combinations of (y_{s,t-1},MouseId,z_{s,1},...,z_{s,p}), m00 contains their position
    v00, m00 = numpy.unique(v0[[0, 1, 2, 3]], return_index=True, axis=0)

    m00 = numpy.append(m00, v0.shape[0])

    v00_tensor = torch.Tensor(v00.tolist())
    v00_tensor = v00_tensor.type(torch.LongTensor)
    m00_diff_tensor = torch.from_numpy(numpy.diff(m00)).unsqueeze(0).t()
    i = 0
    for tensor_value in v00_tensor:
        C[int(tensor_value[3]) - 1][int(tensor_value[2]) - 1][int(tensor_value[0]) - 1][int(tensor_value[1]) - 1] = m00_diff_tensor[i]
        i = i + 1
    sz = C.shape
    print(sz)
    print(C)
    #initialize lambda_exgns: step2
    a = torch.zeros(d0, sz[2])
    print(a.shape)
    print(a)
    # lambda_exgns_mat = torch.zeros(d0, sz[1])
    # a = C
    # a_sum = a.sum(0)
    # a_sum_expanded = a_sum.repeat(5, 1).double()
    # lambda_exgns_mat = torch.div(a, a_sum_expanded)
    # lambda_exgns_mat[lambda_exgns_mat == 0] = 0.0001
    # lambda_exgns_emp = lambda_exgns_mat
    # lambda_exgns = lambda_exgns_emp
    # lambda_exgns_mat_expanded_exgns = lambda_exgns_mat.repeat(1, 6)
    # lambda_exgns_mat_expanded_anmls = lambda_exgns_mat.repeat(1, 2 * numpy.max(MouseId))

    # a = zeros(d0, sz(2));
    # lambda_exgns_mat = zeros(d0, sz(2));
    # for i=1:d0
    # a(i,:)=tenmat(tensor(tenmat(Cdata(i,:), [], 1: (p + 1), [d0 dpreds])), [], 't');
    # end
    # for j=1:sz(2)
    # lambda_exgns_mat(:, j)=gamrnd(a(:, j)+lambdaalpha_exgns * lambda0_mat_expanded_exgns(:, j), 1);
    # lambda_exgns_mat(:, j)=lambda_exgns_mat(:, j) / sum(lambda_exgns_mat(:, j));
    # end
    # lambda_exgns_mat(lambda_exgns_mat == 0) = min(min(lambda_exgns_mat(lambda_exgns_mat > 0)), 0.0001);
    # lambda_exgns_emp = tensor(lambda_exgns_mat, [d0, d0, dpreds]);
    # lambda_exgns = lambda_exgns_emp;



if __name__ == "__main__":
    main()