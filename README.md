# Plane reconstruction from 3D lines

### Overview
![](data/Barn_cluster.png)
This is the code repository implementing the "plane reconstruction from 3D lines" part of the paper "Surface Reconstruction from Multi-view Line Cloud".

### Input
3D line segments set, obj file.

### Output
Planes fitting lines, vg file.

### Algorithm Detail
It can be resolved as a clustering problem like GMM(Gaussian Mixture Model), using Bayes theorem, assume
the probablity of lines is decided by probability of planes and conditional 
probability of lines giving plane.

Here I give the details of obtaining the candidate planes ($\{f_1,f_2,\cdots,f_k\}$, where $k$ is unknown)
from a given set of 3D line segments $\mathcal{L}=\{l_1,l_2,\cdots,l_n\}$. 

#### Geometry representation
For a given line segment, I use the 2 end points to represent it as follow:

$$
l=\mathbf{p}_1:(x_1,y_1,z_1)\rightarrow \mathbf{p}_2:(x_2,y_2,z_2)
$$

As for a plane, I use a point in the plane and the normal to represent it:

$$
f=\{\mathbf{v}:(a,b,c),\,\mathbf{n}:(n_x,n_y,n_z)\}
$$

#### Probability modeling
Assume you already know the $k$ which indicates the number of planes and the probability distribution of those
planes: $\mathrm{P}(f_1),\mathrm{P}(f_2),\cdots,\mathrm{P}(f_k),\sum{_{j=1}}^k \mathrm{P}(f_j)=1$. 
Additionally, I give the conditional probability hypothesis:

$$
\mathrm{P}(l\,| f_j)=\frac1{\sqrt{2\pi}\sigma_j}\exp{{-\frac{[(\mathbf{p}_1-\mathbf{v}_j)\cdot \mathbf{n}_j]^2+[(\mathbf{p}_2-\mathbf{v}_j)\cdot \mathbf{n}_j]^2}{2\sigma_j^2}}}
$$

. Then, you can get the joint probability distribution of the line segment  $l$ and the plane $f_i$ by using Bayes' theorem:

$$
\mathrm{P}(l, f_j)=\mathrm{P}(l\,|f_j)\mathrm{P}(f_j)
$$

The marginal probability is exactly the probability that the line $l$ occurs:

$$
\mathrm{P}(l)=\sum_{j=1}^k\mathrm{P}(l\,|f_j)\mathrm{P}(f_j)
$$

Since you get the probability of each sample line segment and each sample is regarded independent, you will maximize the likelihood function $\mathrm{P}(D|\theta)$ to get parameters of each plane $f_j$:

$$
\max \prod_{i=1}^{n} \mathrm{P}(l_i)
$$

Here I use $\theta$ to denote all parameters in the likelihood function of parameterized model. More details please 
refer to [my blog](https://marktube.github.io/2019/09/19/Line2Plane)

The numerical algorithm for estimating plane parameters is given below:
![2](data/alg.png)

### Dependency
The code is tested on Ubuntu 20.04. To install requirements, use the command below:
```
pip install -r requirements.txt
```


### Usage
use the command below to test the clustering algorithm:
```
python main.py [-h] [--volume VOLUME] [--line_data LINE_DATA] [--out OUT] [--gui GUI] [--sr SR]

```
For more details of options, type the command below:
```
python main.py --help
```
