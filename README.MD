
## CS50 Final project
This is a web app that should be used to track personal expenses. 

The ultimate goal is to give useful insight about our spending abits allowing also to customise the experience including
personal category expense.



### Deployment on python anywhere
In order to deploy the package follow the first_deployment bash file instruction. Also set this inside the web section:
- source code: /home/<your_username>/personal_finance/webapp
- working directory: /home/<your_username>
<br>
and as WSGI configuration:


```
import sys
path = '/home/<your_username>/personal_finance/webapp'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```
