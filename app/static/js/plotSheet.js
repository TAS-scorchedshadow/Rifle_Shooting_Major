$(document).ready(function(){
    const default_range = "700m"
    let data = $('#target-data').data();
    console.log(data);
    let shotList = data.shotlist;
    let range = data.range;
    // Change range to 700m default if the target is longrange (i.e the range is 1000y)
    if (range === "1000y") {
        range = default_range
    }
    let groupX = data.groupx;
    let groupY = data.groupy;
    let groupSize = data.groupsize;
    console.log(shotList);
    var myTarget = new DrawTarget('title',range,shotList,[[groupX, groupY, groupSize]]);


    $("#select-range-span").on('DOMSubtreeModified', function () {
        range = $("#select-range-span").html();
        if (range != "") {
            myTarget.dist = range;
            myTarget.update();
            myTarget.draw();
        }
    });
})