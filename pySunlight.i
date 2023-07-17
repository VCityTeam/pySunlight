/* pySunlight.i */
%module pySunlight

/* WARNING
We must include std library before their c++ includes (std::vector, std::string...),
because they will not be recognized.
https://stackoverflow.com/questions/12236150/string-arguments-are-not-recognized-by-swig */
// String, Vector and Exception support
%include <std_string.i>
%include <std_vector.i>
%include <std_except.i>

%{
    // Specify that the result will be build to a python module 
    // with __init__ function
    #define SWIG_FILE_WITH_INIT

    #include "maths/Vector3.h"
    #include "maths/Ray.h"
    #include "maths/Triangle.h"
    #include "maths/AABB.h"
    #include "maths/RayHit.h"

    #include "cores/API.h"
%}

%include "maths/Vector3.h"
%include "maths/Ray.h"
%include "maths/Triangle.h"
%include "maths/AABB.h"
%include "maths/RayHit.h"

%include "cores/API.h"


/* Instantiate the required template specializations */
%template(TriangleSoup)     std::vector<Triangle>;
%template(BoundingBoxes)    std::vector<AABB>;
%template(RayHits)          std::vector<RayHit>;
%template(Vec3f)            TVec3<float>;
%template(Vec3d)            TVec3<double>;