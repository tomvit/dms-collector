/* Simple http server to simulate dms spy app running on weblogic 10.3.6 
   It provides http basic authentication 
   Tomas Vitvar, tomas@vitvar.com
*/
const http = require('http');
const url = require('url');
const fs = require('fs');

const port = process.argv[2] || 7031;
const mode = process.argv[3] || "";

const username = "weblogic"
const password = "password1"

function sendAuthenticate(req, res) {
  res.statusCode = 401;
  res.setHeader('WWW-Authenticate', 'Basic realm="dms spy simulation"');
  res.end('');  
}

http.createServer(function (req, res) {
  console.log(`${req.method} ${req.url}`);

  // http basic auth
  var auth = req.headers['authorization'];
  
  if (!auth) {
    console.log(`No authorization header!`);
    sendAuthenticate(req, res);
    return;
  } else {
    var buf = new Buffer(auth.split(' ')[1], 'base64');
    var creds = buf.toString().split(':');
    
    if (creds[0] != username || creds[1] != password) {
      console.log(`Invalid credentials!`);
      sendAuthenticate(req, res);
      return;
    }
  }

  // user authenticated
  // parse URL
  var pathname = url.parse(req.url).pathname;
  var queryData = url.parse(req.url, true).query;
  
  filename = "data/" + queryData.table + (queryData.description === "true" ? "_descr" : "_values") + ".xml";
  console.log(`requested file: ${filename}`)

  fs.exists(filename, function (exist) {
    if(!exist) {
      // if the file is not found, return 404
      res.statusCode = 404;
      res.end(`File ${filename} not found!`);
    }

    // read file from file system
    fs.readFile(filename, function(err, data){
      if(err){
        res.statusCode = 500;
        res.end(`Error getting the file: ${err}.`);
      } else {
        // if the file is found, set Content-type and send data
        res.setHeader('Content-type', 'application/xml' );
        res.end(data);
      }
    });
  });

}).listen(parseInt(port));

console.log(`Server listening on port ${port}`);
