# Card Cutting Machine

The Card Cutting Machine is a tool that cuts cards for Policy and Lincoln-Douglas debate. It does this by employing a small handful of techniques from the Machine Learning and Natural Language Processing communities to attempt to learn from how real debaters cut cards and then process cards the same way. 

This project is a continuous work in progress and is not particularly user-friendly or well-organized. It also does not include a standalone application, so if you wish to give the Card Cutting Machine a spin you will have to install Python and the appropriate libraries. 

A pre-trained version of this model, along with a Jupyter notebook with clear instructions on running the machine, will eventually be included in this repository. 

All of the scripts and code used to generate the model are included though, and some of the Verbatim parsing scripts may be useful for your own debate related projects. However, not all of the raw data produced is included, as the word files include nearly all of the 2021-22 College Policy Debate wiki, and the feature vectors generate by BERT ultimatly totaled up to  ~100 GB. Again though, if you wish to replicate my steps the scripts to generate all of the data I produced are included. 