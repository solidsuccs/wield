///
/// \file wieldGammaSurfaceSphere.h
/// \brief Wield::Main::GammaSurfaceSphere
///
/// Input file options
///   - \b Crystal1: Parameters for the upper crystal
///   - \b Crystal2: Parameters for the lower crystal
///   - \b GammaSurfaceSphere: 
///     - (\b X1,\b Y1,\b Z1): Crystollographic axes corresponding to X,Y,Z axes. Two must be specified.
///     - (\b X2,\b Y2,\b Z2): Crystollographic axes corresponding to X,Y,Z axes. Two must be specified.
///     - \b PrePhiRotX: Additional rotation to apply about the X axis
///     - \b PrePhiRotY: Additional rotation to apply about the Y axis
///     - \b PrePhiRotZ: Additional rotation to apply about the Z axis
///     - \b AzimuthMin [0]: Minimum azimuthal angle (angle between orthogonal projection and X axis)
///     - \b AzimuthMin [360]: Maximum azimuthal angle
///     - \b AzimuthResolution [20]: Number of azimuthal points
///     - \b PolarMin [0]: Minimum polar angle (angle from Z axis)
///     - \b PolarMin [180]: Maximum polar angle
///     - \b PolarResolution [20]: Number of theta points
///     - \b Tolerance [0]: Threshold for throwing out terms from the SurfaceIntegral calculation
///     - \b OutputSkip [1]: Number of calculations between showing output visualization
///

#ifndef WIELD_MAIN_GAMMASURFACESPHERE_H
#define WIELD_MAIN_GAMMASURFACESPHERE_H

#include <pthread.h>


#ifdef WIELD_USE_VTK
#include "Utils/VTK/wieldPlotSphere.h"
#endif
#include "Utils/wieldTypes.h"
#include "Utils/wieldRotations.h"
#include "Utils/wieldExceptions.h"
#include "Utils/wieldProgress.h"
#include "SurfaceIntegrate.h"
#include "IO/wieldReaderMacros.h"

#include "Reader.h"

namespace Wield
{
namespace Main
{
struct GammaSurfaceSphere_threadargs
{
  int index;
  int numThreads;
  int outputSkip;
  double a;
  double b;
  double stdDev;
  double tolerance;
  Wield::Series::CosSeries *crystal1;
  Wield::Series::CosSeries *crystal2;
  Matrix3d *omega1;
  Matrix3d *omega2;
  vector<double> *X;
  vector<double> *Y;
  vector<double> *Z;
  vector<double> *vals;
  double prePhiRotX;
  double prePhiRotY;
  double prePhiRotZ;
  bool dynamicPlotting;
#ifdef WIELD_USE_VTK
  Wield::Utils::VTK::PlotSphere *plotSphere;
#endif
};
void *GammaSurfaceSphere_pthread(void *_args )
{
  GammaSurfaceSphere_threadargs *args = (GammaSurfaceSphere_threadargs *)(_args);
  int index                                 = args->index;
  int numThreads                            = args->numThreads;
  int outputSkip                            = args->outputSkip;
  double a                                  = args->a;
  double b                                  = args->b;
  double stdDev                             = args->stdDev;
  double tolerance                          = args->tolerance;
  Wield::Series::CosSeries &crystal1        = *(args->crystal1);
  Wield::Series::CosSeries &crystal2        = *(args->crystal2);
  Matrix3d &omega1                          = *(args->omega1);
  Matrix3d &omega2                          = *(args->omega2);
  vector<double> &X                         = *(args->X);
  vector<double> &Y                         = *(args->Y);
  vector<double> &Z                         = *(args->Z);
  vector<double> &vals                      = *(args->vals);
  double prePhiRotX                         = args->prePhiRotX;
  double prePhiRotY                         = args->prePhiRotY;
  double prePhiRotZ                         = args->prePhiRotZ;
#ifdef WIELD_USE_VTK
  Wield::Utils::VTK::PlotSphere &plotSphere = *(args->plotSphere);
#endif


  // GENERATE GAMMA SURFACE 
  for (int i=0; i<X.size(); i++)
    {
      if ((index == 0) && (!(i % outputSkip) || i==X.size()-1))
      	{
#ifdef WIELD_USE_VTK
	  if (args->dynamicPlotting)
	    plotSphere.SetData(vals);
#endif
      	  WIELD_PROGRESS("Computing gamma surface", i, X.size(), 1);
      	}      

      if ( i%numThreads != index ) continue;

      Eigen::Vector3d n(X[i],Y[i],Z[i]);
      Matrix3d N = 
	createMatrixFromXAngle(prePhiRotX)*
	createMatrixFromYAngle(prePhiRotY)*
	createMatrixFromZAngle(prePhiRotZ)*
	createMatrixFromNormalVector(n);
      double W = a - b*SurfaceIntegrate(crystal1, omega1*N, crystal2, omega2*N, stdDev, tolerance, "cauchy");
      vals[i] = (W);
    }
  if (index==0) cout << endl;
  pthread_exit(_args);
  return NULL;
}

void GammaSurfaceSphere(Reader::Reader &reader, ///< A Reader 
			bool dynamicPlotting = false,
			int numThreads = 1)   ///< Toggle to specify if plot window should show during run
{
  WIELD_EXCEPTION_TRY;

  // FILE INPUT/OUTPUT
  bool printOutput = reader.Find("GammaSurfaceSphere","OutFile");
  ofstream out;

  // READ THE STANDARD VARIABLES
  WIELD_IO_READ_CRYSTAL(1);
  WIELD_IO_READ_CRYSTAL(2);
  WIELD_IO_READ_CRYSTAL_ORIENTATION("GammaSurfaceSphere",1);
  WIELD_IO_READ_CRYSTAL_ORIENTATION("GammaSurfaceSphere",2);
  WIELD_IO_READ_PARAMETERS("GammaSurfaceSphere");
  // ADDITIONAL INTERFACE ROTATION
  double prePhiRotX        = reader.Read<double>("GammaSurfaceSphere","PrePhiRotX",0.);
  double prePhiRotY        = reader.Read<double>("GammaSurfaceSphere","PrePhiRotY",0.);
  double prePhiRotZ        = reader.Read<double>("GammaSurfaceSphere","PrePhiRotZ",0.);		
  // CALCULATION RANGE
  double azimuthResolution = reader.Read<double>("GammaSurfaceSphere", "AzimuthResolution", 20.);
  double azimuthMin        = reader.Read<double>("GammaSurfaceSphere", "AzimuthMin", 0.);
  double azimuthMax        = reader.Read<double>("GammaSurfaceSphere", "AzimuthMax", 360.);
  double polarResolution   = reader.Read<double>("GammaSurfaceSphere", "PolarResolution", 20.);
  double polarMin          = reader.Read<double>("GammaSurfaceSphere", "PolarMin", 0.);
  double polarMax          = reader.Read<double>("GammaSurfaceSphere", "PolarMax", 180.);
  double rResolution       = reader.Read<double>("GammaSurfaceSphere", "RResolution", 20.);
  double rMin              = reader.Read<double>("GammaSurfaceSphere", "RMin", 0.);
  double rMax              = reader.Read<double>("GammaSurfaceSphere", "RMax", 1.);
  // MISC
  double tolerance         = reader.Read<double>("GammaSurfaceSphere","Tolerance",0.);
  int    outputSkip        = reader.Read<int>   ("GammaSurfaceSphere","OutputSkip",1);


  // GENERATE A SPHERE MANUALLY OR USING VTK
  vector<double> X,Y,Z;
#ifdef WIELD_USE_VTK
  Wield::Utils::VTK::PlotSphere *plotSphere;
  if (dynamicPlotting)
    {
      plotSphere = new Wield::Utils::VTK::PlotSphere(azimuthResolution,polarResolution,azimuthMin,azimuthMax,polarMin,polarMax);
      plotSphere->GetPointLocations(X,Y,Z);
    }
  else
#endif
    {
      // Do this if VTK is disabled 
      // OR if VTK is enabled but the user does not want dyanmic plotting
      double dTheta = (azimuthMax - azimuthMin)/(double)azimuthResolution;
      double dPhi = (polarMax - polarMin)/(double)polarResolution;
      double dR   = (rMax - rMin)/(double)rResolution;
      for (double theta = azimuthMin; theta < azimuthMax + dTheta; theta += dTheta) 
	if (reader.Find("GammaSurfaceSphere","RResolution"))
	  for (double r = rMin; r < rMax + dR; r += dR) 
	    {
	      X.push_back(r*cos(theta*pi/180));
	      Y.push_back(r*sin(theta*pi/180));
	      if (1-(r*r) < 0)
		Z.push_back(0.);
	      else 
		Z.push_back(sqrt(1-(r*r)));
	    }
	else
	  for (double phi = polarMin; phi < polarMax + dPhi; phi += dPhi) 
	    {
	      X.push_back(sin(phi*pi/180.)*cos(theta*pi/180.));
	      Y.push_back(sin(phi*pi/180.)*sin(theta*pi/180.));
	      Z.push_back(cos(phi*pi/180.));
	    }
    }
  vector<double> vals(X.size());

  // SPAWN THREADS TO DO HEAVY LIFTING
  GammaSurfaceSphere_threadargs args[numThreads];
  pthread_t threads[numThreads];
  int errorCode;
  for (int i=0; i<numThreads; i++)
    {
      args[i].index            = i;
      args[i].numThreads       = numThreads;
      args[i].outputSkip       = outputSkip;
      args[i].a                = a;
      args[i].b                = b;
      args[i].stdDev           = stdDev;
      args[i].tolerance        = tolerance;
      args[i].crystal1         = &crystal1;
      args[i].crystal2         = &crystal2;
      args[i].omega1           = &omega1;
      args[i].omega2           = &omega2;
      args[i].X                = &X;
      args[i].Y                = &Y;
      args[i].Z                = &Z;
      args[i].vals             = &vals;
      args[i].prePhiRotX       = prePhiRotX;
      args[i].prePhiRotY       = prePhiRotY;
      args[i].prePhiRotZ       = prePhiRotZ;
      args[i].dynamicPlotting  = dynamicPlotting;
#if WIELD_USE_VTK
      args[i].plotSphere       = plotSphere;
#endif

      errorCode = pthread_create(&threads[i], NULL, GammaSurfaceSphere_pthread, (void*)(&args[i]));
      if (errorCode)
	WIELD_EXCEPTION_NEW("Error starting thread #" << i << ": errorCode = " << errorCode);
    }
  for (int i=0; i<numThreads; i++)
    {
      errorCode = pthread_join(threads[i],NULL);
      if (errorCode)
	WIELD_EXCEPTION_NEW("Error joining thread #" << i << ": errorCode = " << errorCode);
    }
  
  // PRINT DATA TO OUTPUT FILE IF SPECIFIED
  if (printOutput) 
    {
      out.open(reader.Read<string>("GammaSurfaceSphere","OutFile").c_str());
      for (int i=0; i<X.size(); i++)
	out << X[i] << " " << Y[i] << " " << Z[i] << " " << vals[i] << endl;
      out.close();
    }

  // CLEAN UP
  WIELD_EXCEPTION_CATCH;
} 
}
}


#endif


