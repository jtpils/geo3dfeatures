import pytest

import numpy as np

from sklearn.decomposition import PCA

from geo3dfeatures.features import (accumulation_2d_neighborhood, triangle_variance_space,
                                    compute_3D_features, compute_2D_features)


SEED = 1337
np.random.seed(SEED)
SIZE = 5000


@pytest.fixture
def line(size=SIZE):
    """Build x,y,z point clouds as a line for 1D features
    """
    data = np.zeros((size, 3))
    data[:, 0] = np.random.uniform(low=1, high=2, size=size)  # x
    # y close to zero
    data[:, 1] = np.random.normal(loc=0, scale=0.002, size=size)
    # z close to zero
    data[:, 2] = np.random.normal(loc=0, scale=0.002, size=size)
    return data


@pytest.fixture
def plane(size=SIZE):
    """Build x,y,z point clouds as a plane for 2D features
    """
    data = np.zeros((size, 3))
    # data[:, 0] = 20 + 2 * np.random.uniform(size=size) - 1  # x
    data[:, 0] = np.random.uniform(low=20, high=22, size=size)  # x
    # data[:, 1] = 40 + 2 * np.random.uniform(size=size) - 1  # y
    data[:, 1] = np.random.uniform(low=40, high=42, size=size)  # y
    data[:, 2] = np.random.normal(loc=5, scale=0.002, size=size)  # z with std close to zero
    return data


@pytest.fixture
def sphere(size=SIZE):
    """Build x,y,z point clouds as a sphere for 3D features
    """
    maxsize = size * 2
    data = np.zeros((maxsize, 3))
    data[:, 0] = np.random.uniform(low=-1, high=1, size=maxsize)  # x
    data[:, 1] = np.random.uniform(low=-1, high=1, size=maxsize)  # y
    data[:, 2] = np.random.uniform(low=-1, high=1, size=maxsize)  # z
    d = data[:, 0] * data[:, 0] + data[:, 1] * data[:, 1] + data[:, 2] * data[:, 2]
    # keep just point inside the sphere
    return data[d <= 1.0][:size]


@pytest.fixture
def ztube(size=SIZE):
    """small x,y variations along z-axis
    """
    data = np.zeros((size, 3))
    # small x variations
    data[:, 0] = np.random.normal(loc=5, scale=0.002, size=size)
    # small y variations
    data[:, 1] = np.random.normal(loc=10, scale=0.002, size=size)
    data[:, 2] = np.random.uniform(low=10, high=14, size=size)  # z
    return data


@pytest.fixture
def wall(size=SIZE):
    """High verticality. Plane projection on (x,y) should look like to a straight line.
    """
    data = np.zeros((size, 3))
    data[:, 0] = np.random.uniform(low=1, high=2, size=size)
    data[:, 1] = 2 + 0.5 * data[:, 0]
    data[:, 2] = np.random.uniform(low=10, high=20, size=size)
    return data


@pytest.fixture
def roof(size=SIZE):
    """Looks like a roof.

    - high elevation
    - plane projection on (x,y) looks like a plane (even a square since max-min are the same of x and y)
    """
    data = np.zeros((size, 3))
    data[:size//2, 0] = np.random.uniform(low=10, high=16, size=size // 2)  # x
    data[:size//2, 1] = np.random.uniform(low=20, high=23, size=size // 2)  # y
    # increase according to y (linearly)
    z0 = 2.
    data[:size//2, 2] = z0 + 1/3 * data[:size//2, 1]
    # translation over y and minus z
    data[size//2:, 0] = np.random.uniform(low=10, high=16, size=size // 2)
    # data[size//2:, 0] = data[:size//2, 0]
    data[size//2:, 1] = 3 + data[:size//2, 1]
    zmax = data[:size//2, 2].max()
    data[size//2:, 2] = 2 * zmax - z0 - 1/3 * data[size//2:, 1]
    return data


def test_accumulation_2d_features(line, plane, sphere):
    acc1D = accumulation_2d_neighborhood(line)
    acc2D = accumulation_2d_neighborhood(plane)
    acc3D = accumulation_2d_neighborhood(sphere)
    # a large density of points for the line
    assert acc1D["count"].mean() > acc2D["count"].mean()
    assert acc1D["count"].mean() > acc3D["count"].mean()
    # low z-std and z-range for line and plane
    assert abs(acc1D["std"].mean() - acc2D["std"].mean()) < 1e-4
    # higher z-std and z-range for sphere
    assert acc3D["std"].mean() > acc1D["std"].mean()
    assert acc3D["std"].mean() > acc2D["std"].mean()
    assert acc3D["z_range"].mean() > acc1D["z_range"].mean()
    assert acc3D["z_range"].mean() > acc2D["z_range"].mean()


def test_sum_triangle_variance_space(plane):
    """Test the values of the barycentric coordinates (variance space).

    The function returns the first two barycentric coordinates but you should have
    `alpha + beta + gamma = 1`
    """
    pca = PCA().fit(plane)
    alpha, beta = triangle_variance_space(pca)
    assert alpha + beta <= 1.0


def test_triangle_variance_space_1D_case(line):
    """Test the values of the barycentric coordinates (variance space).

    'alpha' must be >> to 'beta'
    """
    pca = PCA().fit(line)
    alpha, beta = triangle_variance_space(pca)
    assert alpha > beta
    assert abs(alpha - 1) < 1e-3


def test_triangle_variance_space_2D_case(plane):
    """Test the values of the barycentric coordinates (variance space).

    beta must be > alpha and close to 1.0
    """
    pca = PCA().fit(plane)
    alpha, beta = triangle_variance_space(pca)
    assert alpha < beta
    assert beta >= 0.95


def test_triangle_variance_space_3D_case(sphere):
    """Test the values of the barycentric coordinates (variance space).

    alpha and beta must be close to 0. (so gamme close to 1.)
    """
    pca = PCA().fit(sphere)
    alpha, beta = triangle_variance_space(pca)
    assert 1 - (alpha + beta) >= 0.95


def test_3d_features_line(line):
    """Test curvature change, linearity, planarity and scattering for a line.
    """
    pca = PCA().fit(line)
    curvature_change, linearity, planarity, scattering, *rest = compute_3D_features(
        pca
        )
    # close to 1
    assert linearity >= 0.95
    # close to zero
    assert curvature_change <= 5e-3
    assert planarity <= 0.05
    assert scattering <= 0.05


def test_volume_features_plane(plane):
    """Test curvature change, linearity, planarity and scattering for a plane.
    """
    pca = PCA().fit(plane)
    curvature_change, linearity, planarity, scattering, *rest = compute_3D_features(
        pca
        )
    # close to zero
    assert curvature_change <= 5e-3
    # close to 1
    assert planarity >= 0.95
    # close to 0
    assert linearity <= 0.05
    assert scattering <= 0.05


def test_3d_features_sphere(sphere):
    """Test curvature change, linearity, planarity and scattering for a sphere.
    """
    pca = PCA().fit(sphere)
    curvature_change, linearity, planarity, scattering, *rest = compute_3D_features(
        pca
        )
    # close to 1/3
    assert abs(curvature_change - 1/3) <= 0.05
    # close to 1
    assert scattering >= 0.95
    # close to 0
    assert linearity <= 0.05
    assert planarity <= 0.05


def test_2d_features_ztube(ztube):
    """Projection on (x,y) look like  a tiny noisy circle

    Low and close eigenvalues
    """
    pca = PCA().fit(ztube[:, :2])
    eigensum, ratio = compute_2D_features(pca)
    assert eigensum < 1.0
    assert abs(ratio - 1) <= 0.05


def test_2d_features_wall(wall):
    """Projection on (x,y) look like a straight line

    - High first eigen values. A very big lambda_1 / lambda_2 ratio.
    - The value of the sum is quite close to the first eigen value.
    """
    pca = PCA().fit(wall[:, :2])
    eigenvalues = pca.singular_values_ ** 2
    eigensum, ratio = compute_2D_features(pca)
    assert ratio > 1e10
    assert abs(eigensum - eigenvalues[0]) <= 0.05


def test_2d_features_roof(roof):
    """Projection on (x,y) look like a plane

    - The sum of eigen values is quite high
    - The values of the eigenvalues are almost equal. The ratio is close to 1
    """
    pca = PCA().fit(roof[:, :2])
    eigensum, ratio = compute_2D_features(pca)
    assert abs(ratio - 1) <= 0.05
    assert eigensum > 1000

