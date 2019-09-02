import numpy as np
import LGeometry
import math

class LEM:
    def __init__(self, n_f, limit_min, limit_max):
        '''set initial values for EM algorithm
        n_f: number of faces
        p_f: probability distribution of the faces
        sigma: the standard deviation
        f_v: the point coordinate in each faces
        f_n: the normal vector of each faces
        '''
        self.n_f = n_f * 3
        self.p_f = np.ones(self.n_f)/self.n_f
        self.sigma = np.ones(self.n_f)*math.sqrt(np.sum((limit_max-limit_min)**2))/(n_f*math.sqrt(3))
        self.f_v = np.empty([3,n_f])
        tmp = np.zeros([3, self.n_f])
        for j in range(3):
            self.f_v[j]=np.linspace(limit_min[j],limit_max[j],n_f)
            tmp[j][(j*n_f):(j+1)*n_f] = 1
        self.f_v = np.tile(self.f_v, 3).T
        self.f_n = tmp.T


    def posterior(self,v1,v2,f_j):
        '''
        calculate posterior
        :param v1: vertex which line start
        :param v2: vertex which line end
        :param f_j: face id
        :return: posterior probability
        '''
        dis=-(np.dot((v1-self.f_v[f_j]),self.f_n[f_j])**2+np.dot((v2-self.f_v[f_j]),self.f_n[f_j])**2)/(2*self.sigma[f_j]**2)
        return  self.p_f[f_j]/(math.sqrt(2*math.pi)*self.sigma[f_j])*math.exp(dis)

    def expect(self, lines, vertices):
        '''
        EM algorithm's expectation step
        :param lines: input lines set
        :param vertices: get vertices coordinates from the set
        :return: response of every face
        '''
        response=[]
        for l in lines:
            v1=np.array(l.getVertexCoordinateStart(vertices))
            v2=np.array(l.getVertexCoordinateEnd(vertices))
            post=[]
            for j in range(self.n_f):
                post.append(self.posterior(v1,v2,j))
            post=np.array(post)
            post=post/np.sum(post)
            response.append(post)
        return np.array(response)



    def maximum(self,response,lines,vertices):
        '''
        EM algorithm's maximum step
        :param response: response of every face
        :param lines: input lines set
        :param vertices: get vertices coordinates from the set
        :return: null
        '''
        sqare_error=np.zeros(self.n_f)
        covariance=np.zeros([self.n_f,3,3],dtype=float)
        next_f_v=np.zeros([self.n_f,3],dtype=float)
        for i in range(len(lines)):
            for j in range(self.n_f):
                v1 = np.array(lines[i].getVertexCoordinateStart(vertices))
                v2 = np.array(lines[i].getVertexCoordinateEnd(vertices))
                dis1 = v1-self.f_v[j]
                dis2 = v2-self.f_v[j]
                sqare_error[j] += response[i][j]*(np.dot(dis1,self.f_n[j])**2+np.dot(dis2,self.f_n[j])**2)
                covariance[j] += response[i][j]*(np.multiply(np.mat(dis1),np.mat(dis1).T)+np.multiply(np.mat(dis2),np.mat(dis2).T))
                next_f_v[j] += response[i][j]*(v1+v2)

        resdu = 0
        for j in range(self.n_f):
            s_r=np.sum(response[:,j])
            self.sigma[j]=math.sqrt(sqare_error[j]/s_r)
            new_pf=s_r/len(lines)
            resdu += (self.p_f[j]-new_pf)**2
            self.p_f[j]=new_pf
            self.f_v[j]=next_f_v[j]/(2*s_r)
            w, v=np.linalg.eig(covariance[j])
            self.f_n[j]=v[np.argmin(w)]
        return resdu



    def iter(self, times, lines, vertices):
        '''
        iterator
        :param times: iterator times
        :param lines: input sample lines
        :param vertices: get vertices coordinates from the set
        :return: null
        '''
        print("iteration times:")
        for i in range(times):
            response=self.expect(lines, vertices)
            if(self.maximum(response,lines,vertices)<0.00001):
                break
            print(i+1)