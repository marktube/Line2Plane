import numpy as np
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
import math
import torch

class LEM:
    def __init__(self, volume, limit_min, limit_max):
        '''
        set initial values for EM algorithm
        n_f: number of faces
        p_f: probability distribution of the faces
        sigma: the standard deviation
        f_v: the point coordinate in each faces
        f_n: the normal vector of each faces
        '''
        self.n_f = volume * 3
        self.p_f = np.ones(self.n_f)/self.n_f
        self.sigma = np.ones(self.n_f)*math.sqrt(np.sum((limit_max-limit_min)**2))/(volume*math.sqrt(3))#np.ones(self.n_f)*np.min(limit_max-limit_min)/volume
        self.f_v = np.empty([3,volume])
        tmp = np.zeros([3, self.n_f])
        for j in range(3):
            self.f_v[j]=np.linspace(limit_min[j],limit_max[j],volume)
            tmp[j][(j*volume):(j+1)*volume] = 1
        self.f_v = np.tile(self.f_v, 3).T
        self.f_n = tmp.T
        self.line_count = 0
        self.p1xyz = None
        self.p2xyz = None
        self.coeff = 1/math.sqrt(2*math.pi)

    def l2p_distance(self):
        '''
        calculate the distance to plane by matrix
        :return: the sum of square distance from each 2 points to each plane
        '''
        dis1 = (self.p1xyz - self.f_v) * self.f_n
        dis2 = (self.p2xyz - self.f_v) * self.f_n
        dis = np.square(np.sum(dis1, axis=-1))+np.square(np.sum(dis2, axis=-1))
        return dis

    def v2m(self, vert):
        '''
        transform the vector to a matrix
        :param vert: the input vector as Nxfx3 shape
        :return: the matrix as Nxfx3x3 shape
        '''
        vert = np.expand_dims(vert, axis=-1)
        vert = vert @ vert.transpose((0, 1, 3, 2))
        return vert

    def expect(self, dis):
        '''
        EM algorithm's expectation step
        :param dis: distance for each line points to planes
        :return: response of every face
        '''
        response = 2 * np.square(self.sigma)
        response = dis / response
        response = np.exp(-response)
        response = self.coeff * (response/self.sigma)
        response = response * self.p_f
        s_l = np.sum(response, axis=1)
        response = (response.T / s_l).T
        if np.isnan(response).sum()+np.isinf(response).sum()>0:
            print('error')
        return response

    def maximum(self,response,dis):
        '''
        EM algorithm's maximum step
        :param response: response of every face
        :param dis: distance for each line points to planes
        :return: residual
        '''
        s_r = np.sum(response,axis=0)
        cov = np.sum(response * dis, axis=0) / s_r
        self.sigma = np.sqrt(cov)
        m_n = self.v2m(self.p1xyz - self.f_v) + self.v2m(self.p2xyz - self.f_v)
        m_n = m_n.transpose((2,3,0,1)) * response
        m_n = np.sum(m_n.transpose((2,3,0,1)), axis=0)
        w,v = np.linalg.eig(m_n)
        self.f_n = v[np.arange(v.shape[0]), :, np.argmin(w,axis=-1)]
        pxyz = self.p1xyz + self.p2xyz
        pxyz = pxyz.transpose((2,0,1)) * response
        pxyz = np.sum(pxyz, axis=1) / (2 * s_r)
        self.f_v = pxyz.T
        new_p_f = s_r / self.line_count
        resdu = np.linalg.norm(new_p_f-self.p_f, ord=2)
        self.p_f = new_p_f
        return resdu

    def iter(self, times, p1xyz, p2xyz):
        '''
        iterator
        :param times: iterator times
        :param p1xyz: line end points coordinates
        :param p2xyz: another line end points coordinates
        :return: plane parameters and cluster id for each line
        '''
        self.line_count = p1xyz.shape[0]
        self.p1xyz = np.expand_dims(p1xyz, axis=1)
        self.p1xyz = np.repeat(self.p1xyz, self.n_f, axis=1)
        self.p2xyz = np.expand_dims(p2xyz, axis=1)
        self.p2xyz = np.repeat(self.p2xyz, self.n_f, axis=1)
        for i in range(times):
            dis = self.l2p_distance()
            response = self.expect(dis)
            if(self.maximum(response,dis)<0.000001):
                break
            '''print('=============================iteration %d============================='%(i+1))
            print('sigma - the standard deviation:')
            print(self.sigma)
            print('p_f - probability distribution of the faces:')
            print(self.p_f)'''
        #TODO: use np.unique to drop empty planes
        dis = self.l2p_distance()
        response = self.expect(dis)
        cluster_id = np.argmax(response, axis=1)
        print(np.unique(cluster_id))
        d = -np.sum(self.f_v*self.f_n, axis=1)
        planes = np.column_stack((self.f_v, d))
        return planes, cluster_id
