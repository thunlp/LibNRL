# OpenNE-PyTorch

This is an open-source framework for self-supervised/unsupervised graph embedding implemented by PyTorch, migrated from the earlier version implemented by Tensorflow. 


## Overview
#### New Features

- **A unified framework**: We provide a unified framework for self-supervised/unsupervised node representation learning. Our models include unsupervised network embedding (NE) methods (DeepWalk, Node2vec, HOPE, GraRep, LLE, Lap, TADW, GF, LINE, SDNE) and recent self-supervised graph embedding methods (GAE, VGAE).

- **More datasets**: We provide both unattributed datasets (Wiki, BlogCatalog, Flickr, Wikipedia, PPI) and attributed datasets (Cora, CiteSeer, Pubmed) of all sizes.

- **Efficiency**: We provide faster and more efficient models and better default hyper-parameter settings than those in the previous version. The table below shows 
performances of OpenNE-PyTorch models on Cora Dataset as compared with the previous version, where
 "F1/Accuracy" refers to accuracy in GCN and micro F1-scores in other models, and "Time" refers to training time. 
 Hyperparameters are set to default values unless specified in "Remarks". We also list results of our new models, GAE and VGAE.


<table cellspacing='1' bgcolor='#fefefe'>
<tr>
    <th rowspan="2" bgcolor='#ffffff'>method</th>
    <th colspan="2" bgcolor='#eeeeee'>Time</th>
    <th colspan="2" bgcolor='#eeeeee'>F1/Accuracy</th>
    <th rowspan="2">Remarks</th>
</tr>
<tr bgcolor='#ffffff'>
    <th>OpenNE(old)</th>
    <th>OpenNE-Pytorch</th>
    <th>OpenNE(old)</th>
    <th>OpenNE-Pytorch</th>
</tr>
<tr bgcolor='#eeeeee'>
    <td>DeepWalk</td>
    <td>85.85</td>
    <td><strong>74.98</strong></td>
    <td>.832</td>
    <td>.832</td>
    <td>-</td>
</tr>
<tr bgcolor='#ffffff'>
    <td>Node2vec</td>
    <td>143.67</td>
    <td><strong>38.18</strong></td>
    <td><strong>.814</strong></td>
    <td>.807</td>
    <td>-</td>
</tr>
<tr bgcolor='#eeeeee'>
    <td>HOPE</td>
    <td>2.66</td>
    <td><strong>2.45</strong></td>
    <td>.634</td>
    <td><strong>.743</strong></td>
    <td>-</td>
</tr>
<tr bgcolor='#ffffff'>
    <td>GraRep</td>
    <td>44.27</td>
    <td><strong>4.04</strong></td>
    <td>.770</td>
    <td><strong>.776</strong></td>
    <td>-</td>
</tr>
<tr bgcolor='#eeeeee'>
    <td>TADW</td>
    <td><strong>43.42</strong></td>
    <td>59.12</td>
    <td><strong>.852</strong></td>
    <td>.843</td>
    <td>-</td>
</tr>
<tr bgcolor='#ffffff'>
    <td>GF</td>
    <td><strong>15.01</strong></td>
    <td>19.53</td>
    <td>.546</td>
    <td><strong>.775</strong></td>
    <td>default # epochs changed</td>
</tr>
<tr bgcolor='#eeeeee'>
    <td>LINE</td>
    <td><strong>86.75</strong></td>
    <td>98.69</td>
    <td>.417</td>
    <td><strong>.722</strong></td>
    <td>default # epochs changed</td>
</tr>
<tr bgcolor='#ffffff'>
    <td>SDNE</td>
    <td>195.02</td>
    <td><strong>10.22</strong></td>
    <td>.532</td>
    <td><strong>.742</strong></td>
    <td>-</td>
</tr>
<tr bgcolor='#eeeeee'>
    <td>GCN</td>
    <td>17.4</td>
    <td><strong>11.22</strong></td>
    <td>.857</td>
    <td><strong>.861</strong></td>
    <td rowspan="3">  --sparse  </td>
</tr>
<tr bgcolor='#ffffff'>
    <td>GAE</td>
    <td>-</td>
    <td><strong>55.97</strong></td>
    <td>-</td>
    <td><strong>.788</strong></td>
</tr>
<tr bgcolor='#eeeeee'>
    <td>VGAE</td>
    <td>-</td>
    <td><strong>124.03</strong></td>
    <td>-</td>
    <td><strong>.809</strong></td>
</tr>
</table>

See Experimental Results for performances on Wiki and BlogCatalog.

- **Modularity**: We entangle the codes into three parts: Dataloader, Model and Task. Users can easily customize the datasets, methods and tasks. It is also easy to define their specific datasets and methods.

#### Future Plan
We plan to add more models and tasks in our framework. Our future plan includes:

- More self-supervised models such as ARGA/ARVGA, GALA and AGE.

- New tasks for link prediction, graph clustering and graph classification.

You are welcomed to add your own datasets and methods by proposing new pull requests. 

## Usage
#### Installation

- Clone this repo.
- Enter the directory where you clone it, and run the following code:
    ```bash
    pip install -r requirements.txt
    cd src
    ```
- You can start using OpenNE by simply changing directory to OpenNE/src. 
If instead you want to install OpenNE as a site-package, run the following command in OpenNE/src:
    ```bash
    python setup.py install
    ```

#### Input Instructions

##### Use default values

It is easy to get started with OpenNE. Here are some commands for basic usages with default values:

    python -m openne --model gf --dataset blogcatalog
    python -m openne --model gcn --dataset cora

##### `store_true` and `store_false` parameters

Parameters like `--sparse` have action `store_true`, which means they are `False` by default, 
and should be specified if you want to assign `True`. Run GCN with sparsed matrices by the following command:
    
    python -m openne --model gcn --dataset cora --sparse

You can use `store_false` parameters, eg. `--no-save`, in a similar way:

    python -m openne --model gcn --dataset cora --sparse --no-save
    
OpenNE saves your models and training results to file by default, which may cost longer time. The above command is used when you wish not to save the results.
    
##### Use your own datasets

Use `--local-dataset` (which is also a `store_true` parameter!) and specify 
`--root-dir`, `--edgefile`/`--adjfile`, 
`--labelfile`, `--features` and `--status` to import dataset from file. 

Optionally, specify `store_true` parameters `--weighted` and `--directed` to 
view the graph as weighted and/or directed.

If you wish to use your dataset in "~/mydataset", which includes edges.txt, 
an edgelist file, and labels.txt, a label file, input the following:
    
    python -m openne --model gf --local-dataset --root-dir ~/mydataset --edgefile edges.txt --labelfile labels.txt


##### Input values

While all parameter names must be provided in lower case, string input values are **case insensitive**:

    python -m openne --model SDnE --dataset coRA

The way to provide a Python list (as of `--encoder-layer-list` in SDNE and `--hiddens` in GCN) is input each elements 
separated by spaces:

    python -m openne --model sdne --dataset cora --encoder-layer-list 1000 128
    
##### CUDA and multi-GPU

OpenNE uses CUDA by default if `torch.cuda.is_available() == True`. To disable CUDA, use `--cpu`.

When CUDA is enabled, you can select multiple GPU devices by using `--devices [device_ids]`. `[device_ids]` includes 
a number of integers, on the first of which your model and input are stored. Use `--data-parallel` to utilize
 data parallelism on the chosen devices.

#### General Options

You can check out the other options available to use with *OpenNE* using:

    python -m openne --help

- `--model {deepwalk, line, node2vec, grarep, tadw, gcn, lap, gf, hope and sdne}` the specified NE model;
- `--dataset {ppi, wikipedia, flickr, blogcatalog, wiki, pubmed, cora, citeseer}` standard dataset as provided by OpenNE;

If instead you want to create a dataset from file, you can provide your own graph by using switch
- `--local-dataset` (action `store_true`; mutually exclusive with `--dataset`)

and the following arguments:
- `--root-dir`, root directory of input files. If empty, you should provide absolute paths for graph files;
- `--edgefile`, description of input graph in edgelist format;
- `--adjfile`, description of input graph in adjlist format (mutually exclusive with `--edgefile`);
- `--label-file`, node label file; 
- `--features`, node feature file for certain models (optional);
- `--name`, dataset name, "SelfDefined" by default;
- `--weighted`, view graph as weighted (action `store_true`);
- `--directed`, view graph as directed (action `store_true`);

For general training options:
- `--dim`, dimension of node representation, 128 by default;
- `--clf-ratio`, the ratio of training data for node classification, 0.5 by default;
- `--no-save`, choose not to save the result (action `store_false`, dest=save);
- `--output`, output file for vectors, which will be saved to "results" by default;
- `--sparse`, calculate by sparse matrices (action `store_true`) (only supports lle & gcn);

For models with multiple epochs:
- `--epochs`, number of epochs;
- `--validate`, `True` if validation is needed; by default it is `False` except with GCN;
- `--validation-interval`, number of epochs between two validations, 5 by default;
- `--debug-output-interval`, number of epochs between two debug outputs, 5 by default;

For device options:
- `--cpu`, force OpenNE to run on CPU. Ignored if `torch.cuda.is_available() == False`.
- `--devices`, specify CUDA devices for OpenNE to run on (default 0). Devices other than
`device_id[0]` are ignored except with `--data-parallel`. Ignored if `torch.cuda.is_available() == False`.
- `--data-parallel`, split input batch and perform data parallelism (action `store_true`). Only works 
for methods with `--batch-size` (i.e. line, sdne). 

#### Specific Options

GraphFactorization:
- `--weight-decay`, weight for l2-loss of embedding matrix (1.0 by default);
- `--lr`, learning rate (0.003 by default)

GraRep:

- `--kstep`, use k-step transition probability matrix（requires `dim % kstep == 0`).


HOPE:
- `--measurement {katz, cn, rpr, aa}`  mesurement matrix, `katz` by default;
- `--beta`, parameter with katz measurement, 0.02 by default;
- `--alpha`, parameter with rpr measurement, 0.5 by default;

LINE:
- `--lr`, learning rate, 0.001 by default;
- `--batch-size`, 1024 by default;
- `--negative-ratio`, 5 by default;
- `--order`, 1 for the 1st-order, 2 for the 2nd-order and 3 for 1st + 2nd, 3 by default;

SDNE:

- `--encoder-layer-list`, list of neuron numbers at each encoder layer. 
In SDNE, the last number `--encoder-layer-list`, instead of `--dim`, is the dimension of the output node representation. \[128\] by default;
- `--alpha`, parameter that controls the first-order proximity loss, 1e-6 by default;
- `--beta`, parameter used for construct matrix B, 5 by default;
- `--nu1`, parameter that controls l1-loss of weights in autoencoder, 1e-8 by default;
- `--nu2`, parameter that controls l2-loss of weights in autoencoder, 1e-5 by default;
- `--bs`, batch size, 200 by default;
- `--lr`, learning rate, 0.001 by default;
- `--decay`, allow decay in learning rate (action store_true);

TADW: (requires attributed graph, eg. cora, pubmed, citeseer)
- `--lamb`, parameter that controls the weight of regularization terms, 0.4 by default;

GCN: (requires attributed graph)
- `--lr`, learning rate, 0.01 by default;
- `--dropout`, dropout rate, 0.5 by default;
- `--weight-decay`, weight for l2-loss of embedding matrix, 0.0001 by default;
- `--hiddens`, list of neuron numbers in each hidden layer, \[16\] by default;
- `--max-degree`, maximum Chebyshev polynomial degree. 0 (disable Chebyshev polynomial) by default;

GAE and VGAE: (requires attributed graph) shares the same parameter list with GCN.
- `--lr`, default 0.01;
- `--dropout`, default 0.0;
- `--weight-decay`, default 1e-4;
- `--early-stopping`, default 100;
- `--hiddens`, default \[32\];
- `--max-degree`, default 0;

DeepWalk and node2vec:
- `--num-paths`, number of random walks that starts at each node, 10 by default;
- `--path-length`, length of random walk started at each node, 80 by default;
- `--window`, window size of skip-gram model; 10 by default;
- `--q` (only node2vec), 1.0 by default;
- `--p` (only node2vec), 1.0 by default.

## Experimental Results

We provide experimental results of OpenNE models on Wiki and BlogCatalog datasets. 
For performances on Cora, checkout section "Overview" - "New Features".

Wiki 

| Algorithm | F1-micro | F1-macro | Time | Remarks |
|-----------|----------|----------|------|---------|
| HOPE      | 0.613|	0.432|	1.89| - |
| GF	|0.618	|0.432	|61.22|-|
|GraRep	|0.608	|0.42	|4.33|	-|
Node2vec	|0.656	|0.535|	49.18|	-|
DeepWalk	|0.662	|0.522|	97.47|	-|
SDNE	|0.655	|0.522	|81.19|	-|
LINE	|0.631	|0.488	|234.12|	epochs=40|

BlogCatalog

| Algorithm | F1-micro | F1-macro | Time | Remarks |
|-----------|----------|----------|------|---------|
|HOPE|	0.336|	0.157	|96.63|-|
GF|	0.235|	0.066|	800.02|-|
GraRep|	0.399	|0.233|	103.27|-|
Node2Vec|	0.396	|0.26|	1962.93|-|
DeepWalk|	0.398|	0.261|	516.64|-|
SDNE|	0.372	|0.232|	1323.93|-|
LINE	|0.384	|0.235|	4739.79|-|



## Citing

If you find *OpenNE* is useful for your research, please consider citing the following papers:

    @InProceedings{perozzi2014deepwalk,
      Title                    = {Deepwalk: Online learning of social representations},
      Author                   = {Perozzi, Bryan and Al-Rfou, Rami and Skiena, Steven},
      Booktitle                = {Proceedings of KDD},
      Year                     = {2014},
      Pages                    = {701--710}
    }
    
    @InProceedings{tang2015line,
      Title                    = {Line: Large-scale information network embedding},
      Author                   = {Tang, Jian and Qu, Meng and Wang, Mingzhe and Zhang, Ming and Yan, Jun and Mei, Qiaozhu},
      Booktitle                = {Proceedings of WWW},
      Year                     = {2015},
      Pages                    = {1067--1077}
    }
    
    @InProceedings{grover2016node2vec,
      Title                    = {node2vec: Scalable feature learning for networks},
      Author                   = {Grover, Aditya and Leskovec, Jure},
      Booktitle                = {Proceedings of KDD},
      Year                     = {2016},
      Pages                    = {855--864}
    }
    
    @article{kipf2016semi,
      Title                    = {Semi-Supervised Classification with Graph Convolutional Networks},
      Author                   = {Kipf, Thomas N and Welling, Max},
      journal                  = {arXiv preprint arXiv:1609.02907},
      Year                     = {2016}
    }
    
    @InProceedings{cao2015grarep,
      Title                    = {Grarep: Learning graph representations with global structural information},
      Author                   = {Cao, Shaosheng and Lu, Wei and Xu, Qiongkai},
      Booktitle                = {Proceedings of CIKM},
      Year                     = {2015},
      Pages                    = {891--900}
    }
    
    @InProceedings{yang2015network,
      Title                    = {Network representation learning with rich text information},
      Author                   = {Yang, Cheng and Liu, Zhiyuan and Zhao, Deli and Sun, Maosong and Chang, Edward},
      Booktitle                = {Proceedings of IJCAI},
      Year                     = {2015}
    }
    
    @Article{tu2017network,
      Title                    = {Network representation learning: an overview},
      Author                   = {TU, Cunchao and YANG, Cheng and LIU, Zhiyuan and SUN, Maosong},
      Journal                  = {SCIENTIA SINICA Informationis},
      Volume                   = {47},
      Number                   = {8},
      Pages                    = {980--996},
      Year                     = {2017}
    }
    
    @inproceedings{ou2016asymmetric,
      title                    = {Asymmetric transitivity preserving graph embedding},
      author                   = {Ou, Mingdong and Cui, Peng and Pei, Jian and Zhang, Ziwei and Zhu, Wenwu},
      booktitle                = {Proceedings of the 22nd ACM SIGKDD},
      pages                    = {1105--1114},
      year                     = {2016},
      organization             = {ACM}
    }

    @inproceedings{belkin2002laplacian,
      title                    = {Laplacian eigenmaps and spectral techniques for embedding and clustering},
      author                   = {Belkin, Mikhail and Niyogi, Partha},
      booktitle                = {Advances in neural information processing systems},
      pages                    = {585--591},
      year                     = {2002}
    }

    @inproceedings{ahmed2013distributed,
      title                    = {Distributed large-scale natural graph factorization},
      author                   = {Ahmed, Amr and Shervashidze, Nino and Narayanamurthy, Shravan and Josifovski, Vanja and Smola, Alexander J},
      booktitle                = {Proceedings of the 22nd international conference on World Wide Web},
      pages                    = {37--48},
      year                     = {2013},
      organization             = {ACM}
    }

    @inproceedings{wang2016structural,
      title                    = {Structural deep network embedding},
      author                   = {Wang, Daixin and Cui, Peng and Zhu, Wenwu},
      booktitle                = {Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining},
      pages                    = {1225--1234},
      year                     = {2016},
      organization             = {ACM}
    }
    
    @inproceedings{kipf2016variational,
      title                    = {Variational graph auto-encoders},
      author                   = {Kipf, Thomas N and Welling, Max},
      booktitle                = {NIPS Workshop on Bayesian Deep Learning},
      numpages                 = {3},
      year                     = {2016}
    }
    
## Contributers

The OpenNE-pytorch Project is contributed by [Yufeng Du](https://github.com/Bznkxs), [Ganqu Cui](https://github.com/cgq15) and [Jie Zhou](https://github.com/jayzzhou-thu).

## Project Organizers

- Zhiyuan Liu
  - Tsinghua University
  - [Homepage](http://lzy.thunlp.org/)
 
- Cheng Yang
  - Beijing University of Posts and Telecommunications
  - [Homepage](http://nlp.csai.tsinghua.edu.cn/~yangcheng/)

## Sponsor

This research is supported by Tencent.

<img src="http://logonoid.com/images/tencent-logo.png" width = "300" height = "30" alt="tencent" align=center />

