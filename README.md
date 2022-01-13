# Plane reconstruction from 3D lines

#### Input
3D lines set, obj file.

#### Output
Planes fitting lines, vg file.

#### Algorithm Detail
It can be resolved as a clustering problem like GMM(Gaussian Mixture Model), using Bayes theorem, assume
the probablity of lines is decided by probability of planes and conditional 
probability of lines giving plane.

#### Test Cases
- DJI_cut.obj; 
  - fa2e5729 chaos <liuyanchao99@gmail.com> on 2019/9/19;
  - Volume(61); 
  - Fitting(0.179), Coverage(0.14), Complexity(0.681); 
  - Fitting(0.288), Coverage(0.124), Complexity(0.588);
- line_segments_3d_clustered_allpics_11_5_18.obj; 
  - 33b375de yanchao <liuyanchao99@gmail.com> on 2021/7/6;
  - Volume(19); 
  - Fitting(0.276), Coverage(0.36), Complexity(0.364);
- timber_house_cut.obj;
  - 86c47bfc 刘彦超 <liuyanchao99@gmail.com> on 2020/10/27;
  - Volume(19);
  - Fitting(), Coverage(), Complexity();
- 20_sub_crop.obj;
  - 43397e68 yanchao <liuyanchao99@gmail.com> on 2021/11/9;
  - Volume(19);
  - Fitting(0.308), Coverage(0.331), Complexity(0.361);
- kejilou_crop.obj;
  - 784c15e9 yanchao <liuyanchao99@gmail.com> on 2021/11/24
  - Volume(11);
  - Fitting(0.205), Coverage(0.338), Complexity(0.456);
- Line3D++_kejilou_cut2.obj;
  - 5d3325c7 yanchao <liuyanchao99@gmail.com> on 2021/11/29
  - Volume(11);
  - Fitting(0.212), Coverage(0.312), Complexity(0.477);
- Barn+haoyu_cut[6,7,8].obj;
  - 75fe17c3 yanchao <liuyanchao99@gmail.com> on 2021/12/31
  - Volume([7,9,2]);
  - Fitting(0.205), Coverage(0.338), Complexity(0.456);
