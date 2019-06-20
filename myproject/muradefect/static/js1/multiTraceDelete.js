var trace_num = document.getElementById('trace_num').value

for (var i = 0; i<= trace_num; i++) {
    var id = 'delete' + i;
    var newFunction = document.getElementById(id);
    newFunction.onclick = function(){
//      alert(this.id);
        if ( confirm("Confirm to delete?") ) {
            $.post('/MDI/deleteExploreTable', {'delete': this.id}, function(data){
                $.post("/MDI/plotMultiTrace", function(data) {
                    $("#multiTrace").html(data);
                })
                .error(function() {alert("error129"); });
            });
        };
    };
};