var heatmapInstance = h337.create({
  container: document.getElementById('heatMap')
});
console.log($('#my-data').data('data'));
var testData = {
      max: 10,
      min: 0,
      data: $('#my-data').data('data'),

};
heatmapInstance.setData(testData);