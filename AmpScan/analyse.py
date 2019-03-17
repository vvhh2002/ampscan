# -*- coding: utf-8 -*-
"""
Package for dealing with analysis methods of the ampObject and generating 
reports 
Copyright: Joshua Steer 2018, Joshua.Steer@soton.ac.uk
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
#from .cython_ext import planeEdgeIntersect_cy, logEuPath_cy



class analyseMixin(object):
    r"""
    Analysis methods to act upon a single AmpObject and generate a mpl 
    figure 

    """

    def plot_slices(self, axis=2, slWidth=10):
        r"""
        Generate a mpl figure with information about the AmpObject
        
        Top Left - Slices
        Top Right - Change in cross sectional area through slices
        Bottom Left - Rendering of shape
        Bottom Right - Rendering of shape with values 
        
        TODO: Split this up so each figure is it's own function, top level 
        function to tailor figure to user 
        
        Parameters
        ----------
        axis: int, default 2
            Axis along which to take slices
        slWidth: float, default 10
            Distance between slices
        
        Returns
        -------
        fig: mpl figure
            The mpl figure generated by the function
        ax: tuple
            A tuple of axes used for each subplot in the figure

        """
        # Find the brim edges 
        ind = np.where(self.faceEdges[:,1] == -99999)[0]
        # Define max Z from lowest point on brim
        maxZ = self.vert[self.edges[ind, :], 2].min()
        fig = plt.figure()
        fig.set_size_inches(6, 4.5)

        ax1 = fig.add_subplot(221, projection='3d')
        ax2 = fig.add_subplot(222)
        #Z position of slices 
        slices = np.arange(self.vert[:,2].min() + slWidth,
                           maxZ, slWidth)
        polys = self.create_slices(slices, axis)
        PolyArea = np.zeros([len(polys)])
        for i, poly in enumerate(polys):
            ax1.plot(poly[:,0],
                     poly[:,1],
                     poly[:,2],
                     c='b')
            #SlicePolys[i, :] = poly
            # Compute area of slice
            area = 0.5*np.abs(np.dot(poly[:,0], np.roll(poly[:,1], 1)) -
                              np.dot(poly[:,1], np.roll(poly[:,0], 1)))
            PolyArea[i] = area
        extents = np.array([getattr(ax1, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(ax1, 'set_{}lim'.format(dim))(ctr - r, ctr + r)
        ax1.set_axis_off()
        ax2.plot(slices-slices[0], PolyArea)
        # Rendering of the limb scan
        ax3 = fig.add_subplot(2,2,3)
        Im = self.genIm()
        ax3.imshow(Im, None)
        ax3.set_axis_off()
        # Rendering of the rectification map 
        ax4 = fig.add_subplot(2,2,4)
        self.addActor(CMap = self.CMapN2P)
        Im = self.genIm()
        ax4.imshow(Im, None)
        ax4.set_axis_off()
        plt.tight_layout()
        plt.show()
        return fig, (ax1, ax2, ax3, ax4)
        
    def create_slices(self, slices, axis=2):
        """
        Generate polygons from planar slices through the AmpObject 
        
        Parameters
        ----------
        slices: array_like
            The height of the slice planes
        axis: int, default 2
            The index of the axis to take the slices along
        
        Returns
        -------
        polys: list
            A list of numpy arrays, each array contains the vertices of the 
            polygon generated from the slice

        """
        vE = self.vert[:, axis][self.edges]
        # Find all vertices below plane 
        polys = []
        for i, plane in enumerate(slices):
            ind = vE < plane
            # Select edges with one vertex above and one below the slice plane 
            validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
            validfE = self.faceEdges[validEdgeInd, :].astype(int)
            faceOrder = analyseMixin.logEuPath(validfE)
#            g = defaultdict(set)
#            faceOrder = np.zeros(len(validEdgeInd), dtype=int)
#            # Run eularian path algorithm to order faces
#            for v, w in validfE:
#                g[v].add(w)
#                g[w].add(v)
#            v = validfE[0,0]
#            j=0
#            while True:
#                try:
#                    w = g[v].pop()
#                except KeyError:
#                    break
#                g[w].remove(v)
#                faceOrder[j] = v
#                j+=1
#                v = w
            # Get array of three edges attached to each face
            validEdges = self.edgesFace[faceOrder, :]
            # Remove the edge that is not intersected by the plane
            edges = validEdges[np.isin(validEdges, validEdgeInd)].reshape([-1,2])
            # Remove the duplicate edge from order 
            e = edges.flatten()
#            odx = np.argsort(e)
#            inds = np.arange(1, len(e), 2)
#            row = np.unravel_index(odx, e.shape)[0]
#            mask = np.ones(len(e), dtype=bool)
#            mask[row[inds]] = False
#            sortE = e[mask]
            sortE = []
            for ed in e:
                if ed not in sortE:
                    sortE.append(ed)
            sortE.append(sortE[0])
            # Add first edge to end of array
#            sortE = np.append(sortE, sortE[0])
            sortE = np.asarray(sortE)
            polyEdge = self.edges[sortE]
            EdgePoints = np.c_[self.vert[polyEdge[:,0], :], 
                               self.vert[polyEdge[:,1], :]]
            #Create poly from 
            polys.append(analyseMixin.planeEdgeIntersect_cy(EdgePoints, plane, axis))
        return polys
    
    @staticmethod
    def logEuPath(arr):
        vmax = arr.shape[0]
        rows = list(range(vmax))
        order = np.zeros([vmax], dtype=int)
        i = 0
        val = arr[i, 0]
        nmax = vmax-1
        for n in range(nmax):
            del rows[i]
            order[n] = val
            i=0
            xmax = vmax - n + 1
            for x in rows: 
                if arr[x, 0] == val:
                    val = arr[x, 1]
                    break
                if arr[x, 1] == val:
                    val = arr[x, 0]
                    break
                i+=1
        order[n+1] = val
        return order
    
#    def create_slices_cy(self, slices, axis='Z'):
#        """
#        Another method desc.
#        
#        Attributes
#        ----------
#        
#        slices : array
#            Probably not array
#        axis : arg
#            defaults to Z
#
#        """
#        vE = self.vert[:,2][self.edges]
#        # Find all vertices below plane 
#        polys = []
#        for i, plane in enumerate(slices):
#            ind = vE < plane
#            # Select edges with one vertex above and one below the slice plane 
#            validEdgeInd = np.where(np.logical_xor(ind[:,0], ind[:,1]))[0]
#            validfE = self.faceEdges[validEdgeInd, :].astype(int)
#            faceOrder = logEuPath_cy(validfE)
#            #Get array of three edges attached to each face
#            validEdges = self.edgesFace[faceOrder, :]
#            # Remove the edge that is not intersected by the plane
#            edges = validEdges[np.isin(validEdges, validEdgeInd)].reshape([-1,2])
#            # Remove the duplicate edge from order 
#            e = edges.flatten()
#            odx = np.argsort(e)
#            inds = np.arange(1, len(e), 2)
#            row = np.unravel_index(odx, e.shape)[0]
#            mask = np.ones(len(e), dtype=bool)
#            mask[row[inds]] = False
#            sortE = e[mask]
#            # Add first edge to end of array
#            sortE = np.append(sortE, sortE[0])
#            polyEdge = self.edges[sortE]
#            EdgePoints = np.c_[self.vert[polyEdge[:,0], :], 
#                               self.vert[polyEdge[:,1], :]]
#            # Create poly from
##            polys.append(analyseMixin.planeEdgeintersect(EdgePoints, plane, axis=axis))
#            polys.append(planeEdgeIntersect_cy(EdgePoints, plane, 2))
#        return polys
    @staticmethod
    def planeEdgeIntersect_cy(arr, plane, axisInd):
        emax = arr.shape[0]
        intersectPoints = np.zeros((emax, 3), dtype=np.float32)
        intersectPoints[:, axisInd] = plane
        for i in range(emax):
            for j in range(2):
                e1 = arr[i, j]
                e2 = arr[i, axisInd]
                e3 = arr[i, j+3]
                e4 = arr[i, axisInd+3]
                intersectPoints[i, j] = e1 + (plane - e2) * (e3 - e1) / (e4 - e2)
        return intersectPoints
    
    @staticmethod
    def planeEdgeintersect(edges, plane, axis=2):
        r"""
        Calculate the intersection between a an array of edges and a plane
        
        Parameters 
        ----------
        edges: array_like 
            The edge array which have been calculated to cross the plane
        plane: float
            The height of the plane
        axis: int, default 2
            The index of the axis of the slice
        
        Returns
        -------
        intersectPoints: ndarray
            The intersection points between the edges and the plane
        
        """
        # Allocate intersect points array
        intersectPoints = np.zeros((edges.shape[0], 3))
        # Define the plane of intersect points
        intersectPoints[:, axis] = plane
        axesInd = np.array([0,1,2])[np.array([0,1,2]) != axis]
        for i in axesInd:
            intersectPoints[:, i] = (edges[:, i] +
                                     (plane - edges[:, axis]) *
                                     (edges[:, i+3] - edges[:, i]) /
                                     (edges[:, axis+3] - edges[:, axis]))
        return intersectPoints

