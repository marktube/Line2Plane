#include <RansacShapeDetector.h>
#include <PlanePrimitiveShapeConstructor.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

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
        //std::cout<<line_start<<std::endl;
        if (line_start == '#')
        {
            getline(infs, line);
            //std::cout<<line<<std::endl;
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
            //std::cout<<line<<std::endl;
        }
        else
        {
            getline(infs, line);
            //std::cout<<line<<std::endl;
        }
    }

    pc.setBBox(Vec3f(pmin), Vec3f(pmax));

    infs.close();
    return 0;
}

int main(int argc, char **argv)
{

    PointCloud pc;

    std::cout << "Efficient RANSAC" << std::endl;
    const char *filename = (argc > 1) ? argv[1] : "data/cube.pwn";
    // fill or load point cloud from file
    if (loadPointsFromObj(filename, pc))
    {
        std::cerr << "Error: cannot read file: " << filename << "!" << std::endl;
        return EXIT_FAILURE;
    }

    // ...
    // don't forget to calculate normals
    pc.calcNormals(.005f*pc.getScale());

    RansacShapeDetector::Options ransacOptions;
    ransacOptions.m_epsilon = .005f * pc.getScale();       // set distance threshold to .01f of bounding box width
                                                          // NOTE: Internally the distance threshold is taken as 3 * ransacOptions.m_epsilon!!!
    ransacOptions.m_bitmapEpsilon = .02f * pc.getScale(); // set bitmap resolution to .02f of bounding box width
                                                          // NOTE: This threshold is NOT multiplied internally!
    ransacOptions.m_normalThresh = .8f;                   // this is the cos of the maximal normal deviation
    ransacOptions.m_minSupport = 10;                     // this is the minimal numer of points required for a primitive
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
    std::cout << "remaining points: " << remaining << std::endl;
    std::cout << shapes.size() << " primitives detected." << std::endl;
    return 0;
}
