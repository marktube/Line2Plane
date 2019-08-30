# Plane reconstruction from 3D lines

Input: 3D lines set

Output: Planes fitting lines

It can be resolved as a clustering problem

Algorithm Detail: like GMM(Gaussian Mixture Model), using Bayes theorem, assume
the probablity of lines is decided by probability of planes and conditional 
probability of lines giving plane
