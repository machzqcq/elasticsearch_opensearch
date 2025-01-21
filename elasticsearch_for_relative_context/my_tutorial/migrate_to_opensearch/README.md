# Steps
- Ensure you have elasticsearch, kibana and python client versions 7.10.1
- This might mean creating a new virtualenv just for this exercise
- `python3 -m venv venv` - this was testing with system python==3.11.3 and python==3.8.10
- `source venv/bin/activate`
- if you see this error `AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.` when executing `python3 interns_sample_load.py`, then `pip3 install "numpy<2"`
- `cd ../../` (to elasticsearch folder) and `python3 interns_sample_load.py`
- `path.repo=/usr/share/elasticsearch/snapshots` environment variable in docker-compose
- create snapshot by running `python3 create_snapshot.py` - creates a snapshots directory that contains the snapshots

# Gotchas
- oss versions of elasticsearch and kibana lack features for e.g. menu items on kibana UI, xpack features (so remove any enviroment settings related to xpack etc.)
- elasticsearch python client 7.10.1 says overwrite parameter is not there (params={"overwrite": "true"})
- create `snapshots` directory upfront on host (where elasticsearch writes snapshots to), otherwise if it creates, the ownership will be root:root, and then that folder will not be writeable later and cause all exceptions 