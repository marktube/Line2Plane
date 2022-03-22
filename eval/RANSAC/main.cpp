#include <RansacShapeDetector.h>
#include <PlanePrimitiveShape.h>
#include <PlanePrimitiveShapeConstructor.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>
#include <string.h>
#include <cstring>

float ctrans(float m1, float m2, float hue)
{
    hue = hue - int(hue);
    if (hue < 1.0 / 6.0)
        return m1 + (m2 - m1) * hue * 6.0;

    if (hue < 0.5)
        return m2;

    if (hue < 2.0 / 3.0)
        return m1 + (m2 - m1) * (2.0 / 3.0 - hue) * 6.0;

    return m1;
}

void HLS2RGB(const float *hls, float *rgb)
{
    float m2;
    if (hls[2] == 0.0)
    {
        rgb[0] = hls[1];
        rgb[1] = hls[1];
        rgb[2] = hls[1];
        return;
    }
    if (hls[1] <= 0.5)
        m2 = hls[1] * (1.0 + hls[2]);
    else
        m2 = hls[1] + hls[2] - (hls[1] * hls[2]);

    float m1 = 2.0 * hls[1] - m2;

    rgb[0] = ctrans(m1, m2, hls[0] + 1.0 / 3.0);
    rgb[1] = ctrans(m1, m2, hls[0]);
    rgb[2] = ctrans(m1, m2, hls[0] - 1.0 / 3.0);
}

int getColors(int num_colors, std::vector<Vec3f> &colors)
{
    std::srand((int)std::time(0));
    for (size_t i = 0; i < num_colors; i++)
    {
        float islice = 360.0 / num_colors * i;
        float hls[3] = {islice / 360.0, (50 + rand() / float(RAND_MAX) * 10) / 100,
                        (90 + rand() / float(RAND_MAX) * 10) / 100};
        float rgb[3] = {0.0, 0.0, 0.0};
        HLS2RGB(hls, rgb);
        colors.push_back(Vec3f(rgb));
    }
    return 0;
}

int loadPointsFromXYZ(const char *filename, PointCloud &pc)
{
    std::ifstream infs;
    const float fmax = std::numeric_limits<float>::max();
    const float fmin = -fmax;
    float pmax[3] = {fmin, fmin, fmin};
    float pmin[3] = {fmax, fmax, fmax};

    infs.open(filename, std::ios::in);
    if (!infs.is_open())
        return -1;

    while (!infs.eof())
    {
        float xyz[3];
        infs >> xyz[0] >> xyz[1] >> xyz[2];
        for (size_t i = 0; i < 3; i++)
        {
            if (xyz[i] > pmax[i])
                pmax[i] = xyz[i];
            if (xyz[i] < pmin[i])
                pmin[i] = xyz[i];
        }
        pc.push_back(Point(Vec3f(xyz)));
    }

    pc.setBBox(Vec3f(pmin), Vec3f(pmax));

    infs.close();

    return 0;
}

int loadPointsFromObj(const char *filename, PointCloud &pc)
{
    std::ifstream infs;
    const float fmax = std::numeric_limits<float>::max();
    const float fmin = -fmax;
    float pmax[3] = {fmin, fmin, fmin};
    float pmin[3] = {fmax, fmax, fmax};

    infs.open(filename, std::ios::in);
    if (!infs.is_open())
        return -1;

    while (!infs.eof())
    {
        std::string line;
        char line_start = infs.get();
        // std::cout<<line_start<<std::endl;
        if (line_start == '#')
        {
            getline(infs, line);
            // std::cout<<line<<std::endl;
        }
        else if (line_start == 'v')
        {
            float xyz[3];
            infs >> xyz[0] >> xyz[1] >> xyz[2];
            for (size_t i = 0; i < 3; i++)
            {
                if (xyz[i] > pmax[i])
                    pmax[i] = xyz[i];
                if (xyz[i] < pmin[i])
                    pmin[i] = xyz[i];
            }
            pc.push_back(Point(Vec3f(xyz)));
            getline(infs, line);
            // std::cout<<line<<std::endl;
        }
        else
        {
            getline(infs, line);
            // std::cout<<line<<std::endl;
        }
    }

    pc.setBBox(Vec3f(pmin), Vec3f(pmax));

    infs.close();
    return 0;
}

int savePrimitives(const char *filename, MiscLib::Vector<std::pair<MiscLib::RefCountPtr<PrimitiveShape>, size_t>> &shapes,
                   const PointCloud &pc, int remaining)
{
    std::ofstream outfs;
    outfs.open(filename, std::ios::out);
    if (!outfs.is_open())
        return -1;

    // write the coordinates of the points
    outfs << "num_points: " << pc.size() - remaining << std::endl;
    unsigned int szsum = 0;
    MiscLib::Vector<std::pair<MiscLib::RefCountPtr<PrimitiveShape>, std::size_t>>::const_iterator shape_itr = shapes.begin();
    
    // set output precison
    outfs.flags(std::ios::fixed);
    outfs.precision(6);

    for (; shape_itr != shapes.end(); ++shape_itr)
    {
        unsigned int pend = pc.size() - szsum;
        unsigned int pstart = pc.size() - szsum - shape_itr->second;
        for (size_t i = pstart; i < pend; i++)
        {  
            
            outfs << pc[i].pos.getValue()[0] << " " << pc[i].pos.getValue()[1] << " " << pc[i].pos.getValue()[2] << std::endl;
        }
        szsum += shape_itr->second;
    }

    // write the colors of the points
    outfs << "num_colors: 0" << std::endl;
    std::vector<Vec3f> colors;
    getColors(shapes.size(), colors);
    /*outfs << "num_colors: " << pc.size() - remaining << std::endl;
    szsum = 0;
    for (size_t i = 0; i < shapes.size(); i++)
    {
        unsigned int pend = pc.size() - szsum;
        unsigned int pstart = pc.size() - szsum - shapes[i].second;

        for (size_t j = pstart; j < pend; j++)
        {
            outfs << colors[i].getValue()[0] << " " << colors[i].getValue()[1] << " " << colors[i].getValue()[2] << std::endl;
        }

        szsum += shapes[i].second;
    }*/

    // write the normals of the points
    outfs << "num_normals: 0" << std::endl;
    /*outfs << "num_normals: " << pc.size() - remaining << std::endl;
    szsum = 0;
    for (size_t i = 0; i < shapes.size(); i++)
    {
        const PrimitiveShape *primitive = shapes[i].first;
        unsigned int pend = pc.size() - szsum;
        unsigned int pstart = pc.size() - szsum - shapes[i].second;
        const Plane &pl = dynamic_cast<const PlanePrimitiveShape *>(primitive)->Internal();
        const Vec3f &n = pl.getNormal();
        for (size_t j = pstart; j < pend; j++)
            outfs << n.getValue()[0] << " " << n.getValue()[1] << " " << n.getValue()[2] << std::endl;
        szsum += shapes[i].second;
    }*/

    // now we store the segmentation information
    outfs << "num_groups: " << shapes.size() << std::endl;
    szsum = 0;
    for (size_t i = 0; i < shapes.size(); i++)
    {
        outfs << "group_type: 0" << std::endl;
        outfs << "num_group_parameters: 4" << std::endl;
        const PrimitiveShape *primitive = shapes[i].first;
        const Plane &pl = dynamic_cast<const PlanePrimitiveShape *>(primitive)->Internal();
        const Vec3f &p = pl.getPosition();
        const Vec3f &n = pl.getNormal();
        outfs << "group_parameters: " << n.getValue()[0] << " " << n.getValue()[1] << " " << n.getValue()[2] << " ";
        outfs << -p.dot(n) << std::endl;
        outfs << "group_label: unknown" << std::endl;
        outfs << "group_color: " << colors[i].getValue()[0] << " " << colors[i].getValue()[1]
              << " " << colors[i].getValue()[2] << std::endl;
        outfs << "group_num_points: " << shapes[i].second << std::endl;

        for (size_t j = szsum; j < szsum+shapes[i].second; j++)
            outfs << j << " ";
        outfs << std::endl;
        szsum += shapes[i].second;
        outfs << "num_children: 0" << std::endl;
    }

    outfs.close();
    return 0;
}

int main(int argc, char **argv)
{

    PointCloud pc;

    std::cout << "Efficient RANSAC" << std::endl;
    const char *filename = (argc > 1) ? argv[1] : "data/cube.pwn";
    int fn_len = std::strlen(filename);
    // fill or load point cloud from file
    if (filename[fn_len - 1] == 'j')
    {
        if (loadPointsFromObj(filename, pc))
        {
            std::cerr << "Error: cannot read file: " << filename << "!" << std::endl;
            return EXIT_FAILURE;
        }
    }
    else
    {
        if (loadPointsFromXYZ(filename, pc))
        {
            std::cerr << "Error: cannot read file: " << filename << "!" << std::endl;
            return EXIT_FAILURE;
        }
    }

    // ...
    // don't forget to calculate normals
    pc.calcNormals(.005f * pc.getScale(),16);

    std::clock_t start,stop;
    start = std::clock();
    RansacShapeDetector::Options ransacOptions;
    ransacOptions.m_epsilon = .005f * pc.getScale();      // set distance threshold to .01f of bounding box width
                                                          // NOTE: Internally the distance threshold is taken as 3 * ransacOptions.m_epsilon!!!
    ransacOptions.m_bitmapEpsilon = .02f * pc.getScale(); // set bitmap resolution to .02f of bounding box width
                                                          // NOTE: This threshold is NOT multiplied internally!
    ransacOptions.m_normalThresh = .8f;                   // this is the cos of the maximal normal deviation
    ransacOptions.m_minSupport = 30;                      // this is the minimal numer of points required for a primitive
    ransacOptions.m_probability = .001f;                  // this is the "probability" with which a primitive is overlooked

    RansacShapeDetector detector(ransacOptions); // the detector object

    // set which primitives are to be detected by adding the respective constructors
    detector.Add(new PlanePrimitiveShapeConstructor());

    MiscLib::Vector<std::pair<MiscLib::RefCountPtr<PrimitiveShape>, size_t>> shapes; // stores the detected shapes
    size_t remaining = detector.Detect(pc, 0, pc.size(), &shapes);                   // run detection
                                                                                     // returns number of unassigned points
                                                                                     // the array shapes is filled with pointers to the detected shapes
                                                                                     // the second element per shapes gives the number of points assigned to that primitive (the support)
                                                                                     // the points belonging to the first shape (shapes[0]) have been sorted to the end of pc,
                                                                                     // i.e. into the range [ pc.size() - shapes[0].second, pc.size() )
                                                                                     // the points of shape i are found in the range
                                                                                     // [ pc.size() - \sum_{j=0..i} shapes[j].second, pc.size() - \sum_{j=0..i-1} shapes[j].second )
    stop = std::clock();
    std::cout << "ransac detection used time: " << double(stop - start)/CLOCKS_PER_SEC <<" s"<<std::endl;
    std::cout << "remaining points: " << remaining << std::endl;
    std::cout << shapes.size() << " primitives detected." << std::endl;
    savePrimitives("out.vg", shapes, pc, remaining);
    return 0;
}
