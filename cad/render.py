"""Offscreen VTK renders (software GL, no display needed)."""
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image


def _actor(shape, color, tol=0.3):
    pd = shape.toVtkPolyData(tol, 0.3)
    nrm = vtk.vtkPolyDataNormals(); nrm.SetInputData(pd); nrm.SetFeatureAngle(40); nrm.SplittingOn(); nrm.Update()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(nrm.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m)
    p = a.GetProperty(); p.SetColor(*color); p.SetSpecular(0.3); p.SetSpecularPower(25)
    return a


def render(items, path=None, view=(0.55, -1.0, 0.35), size=(1000, 1000), focal=None, dist=1500.0, angle=30, bg=(1, 1, 1)):
    """items: [(shape, (r,g,b))] in the WORLD frame."""
    ren = vtk.vtkRenderer(); ren.SetBackground(*bg)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.AddRenderer(ren); win.SetSize(*size); win.SetMultiSamples(4)
    for shape, col in items:
        ren.AddActor(_actor(shape, col))
    v = np.array(view, float); v /= np.linalg.norm(v)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*focal); cam.SetPosition(*(np.array(focal) + v * dist)); cam.SetViewUp(0, 0, 1); cam.SetViewAngle(angle)
    ren.ResetCameraClippingRange()
    light = vtk.vtkLight(); light.SetLightTypeToHeadlight(); ren.AddLight(light)
    win.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.ReadFrontBufferOff(); f.Update()
    img = f.GetOutput(); w, h, _ = img.GetDimensions()
    arr = vtk_to_numpy(img.GetPointData().GetScalars()).reshape(h, w, -1)[::-1, :, :3]
    im = Image.fromarray(arr.astype(np.uint8))
    if path:
        im.save(path)
    return im
