

var appTracker  = {};
function getDeatilsofJob(jobid) {
    console.log('I am here');
    console.log(jobid);
    console.log(localStorage.getItem("access_token"));
    const access_token = localStorage.getItem("access_token");
    var params = {
        headers: {
            param0: 'Accept:application/json',
            },
        userId: access_token,
        jobId: jobid
        };
var body = JSON.stringify({"userId": access_token, "jobId":jobid});
var apigClient = apigClientFactory.newClient();
    apigClient.findmyapplicationsGet(params, body)
    .then(function(result){
        console.log(result);
        console.log(result.data.body);
      var data=JSON.parse(result.data.body);
      var outputhtml ="<table bgcolor=\"#FFFFFF\">  <tr> <th>Job id</th><th>Application Date</th> <th>Update</th> <th>Description</th> <th>Add update</th></tr>";

      for(var i=0;i<data.length;i++){
   
               outputhtml += " <tr id = 'r1" + i+"'> <td>" + data[i][0].longValue + "</td>";
               outputhtml += "<td>" + data[i][1].stringValue + "</td>";
               outputhtml += "<td>" + data[i][2].stringValue + "</td>";
               outputhtml += "<td>" + data[i][3].stringValue + "</td>";
               outputhtml += '<td> <button onclick="updateClicked('+data[i][0].longValue+')">Update</button></td> </tr>';
         }
         outputhtml += '</table>'
         document.getElementById("myData").innerHTML = outputhtml;
   

    }).catch( function(result){
      console.log('went to catch')
    });
};

function loadAppTracker(){
    
    console.log(localStorage.getItem("access_token"));
    const access_token = localStorage.getItem("access_token");
    var params = {
        headers: {
            param0: 'Accept:application/json',
            },
            token: access_token
        };
var body = JSON.stringify({"token": access_token});
var apigClient = apigClientFactory.newClient();
    apigClient.findappliedjobsGet(params, body)
    .then(function(result){
        console.log(result);
        console.log(result.data.body);
      var data=JSON.parse(result.data.body);
      var outputhtml ="<table bgcolor=\"#FFFFFF\">  <tr> <th>Job id</th><th>Get Details</th> </tr>";

      for(var i=0;i<data.length;i++){
   
               outputhtml += " <tr id = 'r1" + data[i][0].longValue+"'> <td>" + data[i][0].longValue + "</td>";
               outputhtml += '<td> <button onclick="getDeatilsofJob('+data[i][0].longValue+')">Get Details</button></td> </tr>';
         }
         outputhtml += '</table>'
         document.getElementById("jobdata").innerHTML = outputhtml;
   

    }).catch( function(result){
      console.log('went to catch')
    });
};

function updateClicked(rownum){
    console.log(rownum);
    var outputhtml = ' <p id="updatejobid">Enter Details for job id '+ document.getElementById("r1" + rownum)["cells"]["0"]["innerText"] +'</p><label for="fname">Update:</label><br> \
    <input type="text" id="fname" name="fname"><br> \
    <label for="lname">Description:</label><br> \
    <input type="text" id="lname" name="lname"> \
    <button onclick="submitUpdate('+document.getElementById("r1" + rownum)["cells"]["0"]["innerText"] +')"> Submit </button>';
    document.getElementById("update").innerHTML = outputhtml;
    console.log('update clicked');
};

function submitUpdate(jobid){
    console.log('Entered here')
    var description = document.getElementById("lname").value;
    var update = document.getElementById("fname").value;
    const userId = localStorage.getItem("access_token");
    var params = {
        headers: {
            param0: 'Accept:application/json',
            },
        userId: userId,
        jobId : jobid,
        description : description,
        updateState : update
        };
var body = JSON.stringify({"userId": userId, "jobId" : jobid,
"description" : description,
"updateState" : update});
var apigClient = apigClientFactory.newClient();
    apigClient.updateapplicationPost(params, body)
    .then(function(result){
        console.log(result);
        console.log(result.data.body);
      var data=JSON.parse(result.data.body);
    }).catch( function(result){
      console.log('went to catch')
    });
};