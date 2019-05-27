"""CLI for Geo3Dfeatures

Available choices::
    - geo3d sample [args]
    - geo3d featurize [args]
    - geo3d profiling [args]
    - geo3d kmean [args]
"""

import argparse

from geo3dfeatures import FEATURE_SETS
from geo3dfeatures.tools import (
    info, sample, featurize, profiling, kmean, index
    )

# default value for kd-tree
KD_TREE_LEAF_SIZE = 500


def info_parser(subparser, reference_func):
    """Add arguments for describing a point cloud file

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "info",
        help="Describe an input .las file"
    )
    parser.add_argument("-d", "--datapath",
                        default="./data",
                        help="Data folder on the file system")
    parser.add_argument("-i", "--input-file",
                        required=True,
                        help="Input point cloud file")
    parser.set_defaults(func=reference_func)


def sample_parser(subparser, reference_func):
    """Add arguments focused on data generation process

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "sample",
        help="Extract a sample of a .las file"
    )
    parser.add_argument("-d", "--datapath",
                        default="./data/input",
                        help="Data folder on the file system")
    parser.add_argument("-i", "--input-file",
                        required=True,
                        help="Input point cloud file")
    parser.add_argument('-p', '--sample-points',
                        type=int, required=True,
                        help="Number of sample points to evaluate")
    parser.set_defaults(func=reference_func)


def featurize_parser(subparser, reference_func):
    """Add instance-specific arguments from the command line

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "featurize",
        help="Extract the geometric feature associated to 3D points"
    )
    add_instance_args(parser, featurized=False)
    add_kdtree_args(parser)
    parser.add_argument('-b', '--bin-size',
                        type=float, default=1.0,
                        help="Bin size for accumulation metric computing")
    parser.add_argument('-c', '--extra-columns', nargs="+",
                        help="Extra point cloud feature names (other than x,y,z)")
    parser.add_argument("-i", "--input-file",
                        required=True,
                        help="Input point cloud file")
    parser.add_argument("--chunksize",
                        default=20_000, type=int,
                        help="Number of points in each writing chunk")
    parser.set_defaults(func=reference_func)


def profiling_parser(subparser, reference_func):
    """Add instance-specific arguments from the command line

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "profile",
        help=(
            "Extract in a human-readable format the "
            "geometric feature extraction time measurements"
        )
    )
    parser.add_argument("-e", "--experiment",
                        required=True,
                        help="Name of the feature extraction experiment")
    parser.add_argument("-F", "--file-format",
                        choices=["csv", "json"], default="csv",
                        help="Timer file format")
    parser.set_defaults(func=reference_func)


def kmean_parser(subparser, reference_func):
    """Add instance-specific arguments from the command line

    Build a high-resolution image labelling by predicting semantic segmentation
    labels on image patches, and by postprocessing resulting arrays so as to
    get geographic entities.

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "cluster",
        help="Cluster a set of 3D points with a k-means algorithm"
    )
    add_instance_args(parser, featurized=True)
    parser.add_argument("-k", "--nb-clusters",
                        type=int, required=True,
                        help="Desired amount of clusters")
    parser.set_defaults(func=reference_func)


def index_parser(subparser, reference_func):
    """Index a point cloud scene.

    Parameters
    ----------
    subparser : argparser.parser.SubParsersAction
    reference_func : function
    """
    parser = subparser.add_parser(
        "index",
        help="Index a point cloud file and serialize it"
    )
    add_kdtree_args(parser)
    parser.add_argument("-d", "--datapath",
                        default="./data",
                        help="Data folder on the file system")
    parser.add_argument("-e", "--experiment",
                        help="Name of the feature extraction experiment")
    parser.add_argument("-i", "--input-file",
                        required=True,
                        help="Input point cloud file")
    parser.set_defaults(func=reference_func)


def add_kdtree_args(parser):
    """Add arguments related to kd-tree serialization

    Parameters
    ----------
    parser : argparse.ArgumentParser
    """
    parser.add_argument("--tree-file",
                        help="kd-tree serialized file")
    parser.add_argument('-t', '--kdtree-leafs',
                        type=int, default=KD_TREE_LEAF_SIZE,
                        help="Number of leafs in KD-tree")


def add_instance_args(parser, featurized=True):
    """Add a bunch of command arguments that permits to identify the instance
    of interest

    Parameters
    ----------
    parser : argparse.ArgumentParser
    featurized : bool
        True if the function is called by the featurization program, hence some
        arguments are required; false otherwise
    """
    parser.add_argument("-d", "--datapath",
                        default="./data",
                        help="Data folder on the file system")
    parser.add_argument("-e", "--experiment",
                        required=featurized,
                        help="Name of the feature extraction experiment")
    parser.add_argument('-f', '--feature-set',
                        choices=FEATURE_SETS, default="full",
                        help="Set of computed features")
    parser.add_argument("-m", "--nb-process",
                        type=int, default=2,
                        help="")
    parser.add_argument('-p', '--sample-points',
                        type=int,
                        required=featurized,
                        help="Number of sample points to evaluate")
    neighbor_group = parser.add_mutually_exclusive_group()
    neighbor_group.add_argument('-n', '--neighbors',
                                type=int,
                                help="Number of neighbors to consider. "
                                "Alternative neighborhood definition: "
                                "--radius.")
    neighbor_group.add_argument('-r', '--radius',
                                type=float,
                                help=(
                                    "Radius that defines the neighboring "
                                    "ball. Alternative neighborhood "
                                    "definition: --neighbors."
                                ))


def main():
    """Main method of the module
    """
    parser = argparse.ArgumentParser(
        prog="geo3d",
        description="Geo3dfeatures framework for 3D semantic analysis",
    )
    sub_parsers = parser.add_subparsers(dest="command")
    info_parser(sub_parsers, reference_func=info.main)
    sample_parser(sub_parsers, reference_func=sample.main)
    index_parser(sub_parsers, reference_func=index.main)
    featurize_parser(sub_parsers, reference_func=featurize.main)
    profiling_parser(sub_parsers, reference_func=profiling.main)
    kmean_parser(sub_parsers, reference_func=kmean.main)
    args = parser.parse_args()

    if args.func:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
