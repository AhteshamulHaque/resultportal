
if(sessionStorage.compare == undefined || sessionStorage.compare.length == 0) {
  //do something errornous
  //if this is executed means there was a direct request to this page..
  console.log("Not a valid selection");
}

var me = sessionStorage;
var sem = me.course + "_" + me.branch_initials + "_" + me.compare_sem;
rolls = me.compare.split(',');
console.log(sem);

var request = window.indexedDB.open(me['year']);

request.onsuccess = function(event) {
  var db = event.target.result;
  var tx = db.transaction([sem], "readonly");
  var store = tx.objectStore(sem);

  var res = store.get(me['roll']);

  res.onsuccess = function(event) {
    var my_result = event.target.result;

    for(var i = 0; i < rolls.length; ++i) {
      var new_res = store.get(rolls[i]);

      new_res.onsuccess = function(event) {
        var lose = 0;
        var win = 0;

        var his_result = event.target.result;
        var text = '<div class = "ui container" style = "max-width: 800px !important; margin-bottom: 20px !important"><div class="ui mini attached message" style = "position: relative !important"><div class="header"><div class = "ui two column very relaxed center aligned grid" style = "font-size: 14px !important"><div class = "column">'+ my_result['name'] + "("+ my_result['roll']+")" + '</div><div class = "column">'+ his_result['name']+ '('+his_result['roll']+')'+'</div></div><div class = "ui vertical divider">VS</div></div></div>';
        text += ' <div class="ui attached fluid segment"><div id = "comparision" class = "ui container" style = "max-width: 600px !important">';

        //may have different his_codes variable....I don't know how
        for(var his_code in his_result['result']) {
          for(var my_code in my_result['result']) {

            if(his_result['result'][his_code]['subject'] == my_result['result'][my_code]['subject'] && parseFloat(his_result['result'][his_code]['total']) <= parseFloat(my_result['result'][my_code]['total'])) {
              text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui red left horizontal label" style = "float: left">'+my_result['result'][my_code]['total']+'</div></div><div class = "twelve wide column"><span>'+his_result['result'][his_code]['subject']+'</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+his_result['result'][his_code]['total']+'</div></div></div></div>';
              win += 1;
            }
            else
            if(his_result['result'][his_code]['subject'] == my_result['result'][my_code]['subject'] && parseFloat(his_result['result'][his_code]['total']) > parseFloat(my_result['result'][my_code]['total'])) {
              text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui green left horizontal label" style = "float: left">'+my_result['result'][my_code]['total']+'</div></div><div class = "twelve wide column"><span>'+his_result['result'][his_code]['subject']+'</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+his_result['result'][his_code]['total']+'</div></div></div></div>';
              lose += 1;
            }

          }

        }

        if(parseFloat(his_result['sgpa']) <= parseFloat(my_result['sgpa']))
          text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui red left horizontal label" style = "float: left">'+Number(my_result['sgpa']).toFixed(2)+'</div></div><div class = "twelve wide column"><span>SGPA</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+Number(his_result['sgpa']).toFixed(2)+'</div></div></div></div>';
        else
          text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui green left horizontal label" style = "float: left">'+Number(my_result['sgpa']).toFixed(2)+'</div></div><div class = "twelve wide column"><span>SGPA</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+Number(his_result['sgpa']).toFixed(2)+'</div></div></div></div>';

        if(parseFloat(his_result['cgpa']) <= parseFloat(my_result['cgpa']))
          text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui red left horizontal label" style = "float: left">'+Number(my_result['cgpa']).toFixed(2)+'</div></div><div class = "twelve wide column"><span>CGPA</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+Number(his_result['cgpa']).toFixed(2)+'</div></div></div></div>';
        else
          text += '<div class = "ui mini text center aligned segment" style = "padding: 5px"><div class = "ui grid"><div class = "two wide column"><div class="ui green left horizontal label" style = "float: left">'+Number(my_result['cgpa']).toFixed(2)+'</div></div><div class = "twelve wide column"><span>CGPA</span></div><div class = "two wide column"><div class="ui grey secondary horizontal label" style = "float: right">'+Number(his_result['cgpa']).toFixed(2)+'</div></div></div></div>';
        text += '</div></div><div class="ui bottom attached warning message"><i class="icon help"></i>Already signed up? <span href="#">Login here</span> instead.</div></div></div></div></div>';

        $("#main-content").append(text);
      }
    }
  }
}
