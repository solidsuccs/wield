#!python
import argparse
from math import atan2
from numpy import loadtxt, linspace, meshgrid, arctan2, pi, radians,degrees,concatenate,cos,sin,sqrt
from scipy.interpolate import griddata, interp2d
from pylab import subplots,contourf,pcolor,figure,draw,ginput,show,colorbar,pcolormesh,savefig,plot,ion,pause,clf,xlim,tight_layout,xticks,yticks,set_cmap,get_cmap
from fractional_polar_axes import *
import sys

parser = argparse.ArgumentParser(description='Create a polar surface plot');
parser.add_argument('file', help='Data file for plotting');
parser.add_argument('-r', '--resolution', nargs=2, default=[100,100], help='Resolution in the r and theta directions, respectively')
parser.add_argument('-l', '--theta-limit', nargs=2, default=[-180,180], help='Maximum polar angle')
parser.add_argument('-x', '--x-symmetry', dest='xsim', action='store_true', help='Reflect along the x axis');
parser.add_argument('-y', '--y-symmetry', dest='ysim', action='store_true', help='Reflect along the y axis');
parser.add_argument('-i', '--interactive', dest='interactive', action='store_true', help='Interactive facet investigator');
parser.add_argument('-c', '--center-point', dest='center_point', action='store_true', help='Plot a white dot at the origin');
parser.add_argument('-m', '--method', default='nearest', help='Interpolation method: options are nearest, linear, cubic');
parser.add_argument('-n1','--n1', nargs=2, default=[0,2], help='First Facet vector');
parser.add_argument('-n2','--n2', nargs=2, default=[0,2], help='Second Facet vector');
parser.add_argument('-n3','--n3', nargs=2, default=[0,2], help='Third Facet vector');
parser.add_argument('-f', '--facet-file', default="", help='Facet data input file');
parser.add_argument('-f2', '--facet2-file', default="", help='Facet2 data input file');
parser.add_argument('-f3', '--facet3-file', default="", help='Facet3 data input file');
parser.add_argument('-f4', '--facet4-file', default="", help='Facet4 data input file');
parser.add_argument('-f8', '--facet8-file', default="", help='Facet8 data input file');
parser.add_argument('-o', '--output-file', default="", help='Image output file');
parser.add_argument('-a', '--multiplier', nargs=1, default=[1], help='Multiplier')
parser.add_argument('--tick-locs',nargs='*',default=[]);
parser.add_argument('--tick-labels',nargs='*',default=[]);
parser.add_argument('--center-tick-label',default='');
parser.add_argument('-cmin', '--cmin', default=0,help='Colorbar minimum value');
parser.add_argument('-cmax','--cmax', default=0,help='Colorbar maximum value');
parser.add_argument('-cmap','--cmap', default='jet',help='(jet,gray,binary) See http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps for other values');
args=parser.parse_args();

if (len(args.tick_locs) != len(args.tick_labels)):
    raise Exception("Different number of tick locs than tick labels");
    
data = loadtxt(args.file);
x = data[:,0];
y = data[:,1];
w = float(args.multiplier[0])*data[:,3];

if args.xsim:
    x = concatenate([x,x])
    y = concatenate([y,-y])
    w = concatenate([w,w])
if args.ysim:
    x = concatenate([x,-x])
    y = concatenate([y,y])
    w = concatenate([w,w])

rgrid = linspace(0.0,1,args.resolution[0])
thetagrid = linspace(float(args.theta_limit[0]),float(args.theta_limit[1]),args.resolution[1])
rgrid, thetagrid = meshgrid(rgrid,thetagrid)
wgrid   = griddata((x,y),w,(rgrid*cos(radians(thetagrid)),rgrid*sin(radians(thetagrid))),fill_value=0,method=args.method);


#if float(args.theta_limit[1])-float(args.theta_limit[0]) > 180:
fig,ax = subplots(ncols=1,subplot_kw=dict(projection='polar'))
ax.xaxis.set_ticklabels([])
ax.yaxis.set_ticklabels([])
ax.set_xlim(0,1);
pc = pcolormesh(radians(thetagrid),rgrid,wgrid,shading='gouraud',cmap=get_cmap(args.cmap));
if (len(args.tick_locs) > 0):
    cb = colorbar(pc,pad=0.2,shrink=.8);
else:
    cb = colorbar(pc,pad=0.05,shrink=.9);
if args.cmin != args.cmax:
    cb.set_clim(args.cmin,args.cmax);
# else:
#     fig = figure()
#     ax = fractional_polar_axes(fig,thlim=(float(args.theta_limit[0]),float(args.theta_limit[1])),rlim=(0.0,1))
#     pc = pcolormesh(thetagrid,rgrid,wgrid,shading='gouraud');
#     colorbar(pc)


if (len(args.tick_locs)>0):
    tickLocs = (); tickLabels = ();
    for loc in args.tick_locs:
        tickLocs = (float(loc),) + tickLocs;
    for label in args.tick_labels:
        tickLabels = (r'$'+label+'$',)+tickLabels;
    print(tickLocs);
    print(tickLabels);
    xticks(radians(tickLocs),tickLabels,fontsize='25');
    #
    ax.set_thetagrids(tickLocs,frac=1.2);
if (args.center_tick_label != ""):
    yticks((0.,0.1),(r'$'+args.center_tick_label+'$',''),fontsize='25')


rr = []; tt = [];
if float(args.n1[0])**2 + float(args.n1[1])**2 <= 1:
    rr.append(sqrt(float(args.n1[0])**2 + float(args.n1[1])**2))
    tt.append(atan2(float(args.n1[1]),float(args.n1[0])))
    if float(args.n2[0])**2 + float(args.n2[1])**2 <= 1:
        rr.append(sqrt(float(args.n2[0])**2 + float(args.n2[1])**2))
        tt.append(atan2(float(args.n2[1]),float(args.n2[0])))
        if float(args.n3[0])**2 + float(args.n3[1])**2 <= 1:
            rr.append(sqrt(float(args.n3[0])**2 + float(args.n3[1])**2))
            tt.append(atan2(float(args.n3[1]),float(args.n3[0])))
    rr.append(sqrt(float(args.n1[0])**2 + float(args.n1[1])**2))
    tt.append(atan2(float(args.n1[1]),float(args.n1[0])))
    plot(tt,rr,marker='o');
    xlim(0,1);

if args.facet_file != "":
    rr = []; tt = []; lamb = []
    n1=[]; n2=[]; n3=[];
    file=open(args.facet_file,'r');
    file.readline(); #skip past energy
    lambStr = file.readline().split(); #skip past lambda
    lamb.append(float(lambStr[0]));
    lamb.append(float(lambStr[1]));
    lamb.append(float(lambStr[2]));

    xStr = file.readline().split();
    yStr = file.readline().split();
    n1.append(float(xStr[0])); n2.append(float(xStr[1])); n3.append(float(xStr[2]))
    n1.append(float(yStr[0])); n2.append(float(yStr[1])); n3.append(float(yStr[2]))

    if (lamb[0] > 1E-6):
        rr.append(sqrt(float(n1[0])**2 + float(n1[1])**2))
        tt.append(atan2(float(n1[1]),float(n1[0])))

    if (lamb[1] > 1E-6):
        rr.append(sqrt(float(n2[0])**2 + float(n2[1])**2))
        tt.append(atan2(float(n2[1]),float(n2[0])))

    if (lamb[2] > 1E-6):
        rr.append(sqrt(float(n3[0])**2 + float(n3[1])**2))
        tt.append(atan2(float(n3[1]),float(n3[0])))

    if (lamb[0] > 1E-6):
        rr.append(sqrt(float(n1[0])**2 + float(n1[1])**2))
        tt.append(atan2(float(n1[1]),float(n1[0])))

    plot(tt,rr,marker='o',color='black');
    xlim(0,1);

if args.facet3_file != "":
    rr = []; tt = []; lamb = []
    n1=[]; n2=[]; n3=[];
    file=open(args.facet3_file,'r');
    file.readline(); #skip past energy
    lambStr = file.readline().split(); #skip past lambda
    lamb.append(float(lambStr[0]));
    lamb.append(float(lambStr[1]));
    lamb.append(float(lambStr[2]));

    xStr = file.readline().split();
    yStr = file.readline().split();
    n1.append(float(xStr[0])); n2.append(float(xStr[1])); n3.append(float(xStr[2]))
    n1.append(float(yStr[0])); n2.append(float(yStr[1])); n3.append(float(yStr[2]))

    if (lamb[0] > 1E-6):
        rr.append(sqrt(float(n1[0])**2 + float(n1[1])**2))
        tt.append(atan2(float(n1[1]),float(n1[0])))

    if (lamb[1] > 1E-6):
        rr.append(sqrt(float(n2[0])**2 + float(n2[1])**2))
        tt.append(atan2(float(n2[1]),float(n2[0])))

    if (lamb[2] > 1E-6):
        rr.append(sqrt(float(n3[0])**2 + float(n3[1])**2))
        tt.append(atan2(float(n3[1]),float(n3[0])))

    if (lamb[0] > 1E-6):
        rr.append(sqrt(float(n1[0])**2 + float(n1[1])**2))
        tt.append(atan2(float(n1[1]),float(n1[0])))

    plot(tt,rr,marker='o',color='blue');
    xlim(0,1);

if args.facet4_file != "":
    rr = []; tt = []; lamb = []
    n1=[]; n3=[];
    file=open(args.facet4_file,'r');
    file.readline(); #skip past energy
    lambStr = file.readline().split(); #skip past lambda
    lamb.append(float(lambStr[0]));
    lamb.append(float(lambStr[1]));
    lamb.append(float(lambStr[2]));

    xStr = file.readline().split();
    yStr = file.readline().split();

    if abs(lamb[0]) < 1e-4:
        print('A: ', 0%3);
        n1.append(float(xStr[1])); n1.append(float(yStr[1]));
        n3.append(float(xStr[2])); n3.append(float(yStr[2]));
    elif abs(lamb[1]) < 1e-4:
        print('B');
        n1.append(float(xStr[2])); n1.append(float(yStr[2]));
        n3.append(float(xStr[0])); n3.append(float(yStr[0]));
    elif abs(lamb[2]) < 1e-4:
        print('C');
        n1.append(float(xStr[0])); n1.append(float(yStr[0]));
        n3.append(float(xStr[1])); n3.append(float(yStr[1]));
    else:
        raise Exception('More than two non-zero lambdas')

    rotMatrix = [[0,1],[-1,0]];
    n2 = [n1[1],-n1[0]];
    n4 = [n3[1],-n3[0]];

    for n in [n1,n2,n3,n4,n1]:
        rr.append(sqrt(float(n[0])**2 + float(n[1])**2))
        tt.append(atan2(float(n[1]),float(n[0])))
    print(rr,tt);

    plot(tt,rr,marker='o',color='blue',linewidth='1');
    xlim(0,1);

if args.facet8_file != "":
    rr = []; tt = []; n = [];
    file=open(args.facet8_file,'r');
    file.readline(); #skip past energy
    file.readline(); #skip past lambda
    xStr = file.readline().split();
    yStr = file.readline().split();
    n.append(float(xStr[1])); n.append(float(yStr[1]));

    R = [[0.7071067811870,0.7071067811870],[-0.7071067811870,0.7071067811870]];
    for i in range(0,9):
        n = [R[0][0]*n[0] + R[0][1]*n[1], R[1][0]*n[0] + R[1][1]*n[1]];
        rr.append(sqrt(float(n[0])**2 + float(n[1])**2))
        tt.append(atan2(float(n[1]),float(n[0])))

    plot(tt,rr,marker='o',color='black',linewidth='1');
    xlim(0,1);

if args.center_point:
    plot(0,0,color='white',marker='o');

if args.output_file != "":
    savefig(args.output_file);
elif args.interactive:
    ion();
    #tight_layout()
    show(); pause(1);

    while True:
        io = input("Enter a command: ")
        if (io == 'q'):
            exit();
        if (io == '1'):
            print(griddata((x,y),w,(0,0),fill_value=0,method=args.method));
        if (io == '3'):
            pts = ginput(3,timeout=-1);
            n = np.array([[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])
            e = np.array([0.,0.,1.])
            print(pts);

            n[0][0] = cos(pts[0][0])*pts[0][1]; n[1][0] = sin(pts[0][0])*pts[0][1];  n[2][0] = sqrt(1 - n[0][0]**2 - n[1][0]**2);
            n[0][1] = cos(pts[1][0])*pts[1][1]; n[1][1] = sin(pts[1][0])*pts[1][1];  n[2][1] = sqrt(1 - n[0][1]**2 - n[1][1]**2);
            n[0][2] = cos(pts[2][0])*pts[2][1]; n[1][2] = sin(pts[2][0])*pts[2][1];  n[2][2] = sqrt(1 - n[0][2]**2 - n[1][2]**2);

            lamb = np.linalg.solve(n,e);

            print (n);
            print (lamb);
            print ("Wc = ", 
                   lamb[0]*griddata((x,y),w,(n[0][0], n[1][0]),fill_value=0,method=args.method) +
                   lamb[1]*griddata((x,y),w,(n[0][1], n[1][1]),fill_value=0,method=args.method) +
                   lamb[2]*griddata((x,y),w,(n[0][2], n[1][2]),fill_value=0,method=args.method))

            tt = [pts[0][0],pts[1][0],pts[2][0],pts[0][0]];
            rr = [pts[0][1],pts[1][1],pts[2][1],pts[0][1]];
            plot(tt,rr,marker='o');
            xlim(0,1);
            show(); pause(1);
            #print(griddata((x,y),w,(cos(pts[0][0])*pts[0][1], sin(pts[0][0])*pts[0][1]),fill_value=0,method=args.method));
    show()
else:
    show()

