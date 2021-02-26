//By Henry Guo
//Requires targetDiagram or won't work becuase GroupDiagram uses the Circle object
var target_details = {"details": ['V', '5', '4', '3', '2', '1'],
                  "300m": [300, 70, 140, 280, 420, 600, 1200],
                  "400m": [400, 95, 185, 375, 560, 800, 1800],
                  "500m": [500, 145, 290, 660, 1000, 1320, 1800],
                  "600m": [600, 160, 320, 660, 1000, 1320, 1800],
                  "700m": [700, 255, 510, 815, 1120, 1830, 2400],
                  "800m": [700, 255, 510, 815, 1120, 1830, 2400],
                  "300yds": [274.32, 65, 130, 260, 390, 560],
                  "400yds": [365.76, 85, 175, 350, 520, 745],
                  "500yds": [457.20, 130, 260, 600, 915, 1320],
                  "600yds": [548.64, 145, 290, 600, 915, 1320]
};
var pointScale = 50

function GroupDiagram(myStages, otherStages, stage, canvasId) {
    this.dist = stage[2];
    this.canvasObj = document.getElementById(canvasId);
    let rect = this.canvasObj.parentNode.getBoundingClientRect();
    this.canvasObj.width = rect.width;
    this.canvasObj.height = rect.width;
    this.x = this.canvasObj.width / 2;
    this.y = this.canvasObj.height / 2;
    this.c = this.canvasObj.getContext('2d');
    this.circleRadius = this.canvasObj.width / pointScale;
    this.ratio = this.canvasObj.width/target_details[this.dist][5];
    this.targetBackground = new Circle(this.c, this.x, this.y, this.canvasObj.width/2, targetFill);
    this.points = [];
    let canvasParent = this.canvasObj.parentNode;
    for (let i=0; i<myStages.length; i++){
        let point = new Circle(this.c, this.x + (myStages[i]['groupX']*this.ratio), this.y - (myStages[i]['groupY']*this.ratio), this.circleRadius, 'green', 'black', 0);
        this.points.push(point);
    }
    for (let i=0; i<otherStages.length; i++){
        let point = new Circle(this.c, this.x + (otherStages[i]['groupX']*this.ratio), this.y - (otherStages[i]['groupY']*this.ratio), this.circleRadius, 'red', 'black', 0);
        this.points.push(point);
    }
    this.selectedStage = new Circle(this.c, this.x + (stage[0]*this.ratio), this.y - (stage[1]*this.ratio), this.circleRadius, 'black', 'black', 0 );
    this.points.push(this.selectedStage);
    this.ratio = this.canvasObj.width/target_details[this.dist][5];
    this.draw = function() {
        this.targetBackground.draw();
        for (let i=0; i<this.points.length; i++){
            this.points[i].draw()
        }
        this.c.lineWidth = 2
        this.c.beginPath();
        this.c.moveTo(this.x, 0);
        this.c.lineTo(this.x, this.canvasObj.height);
        this.c.stroke()
        this.c.moveTo(this.canvasObj.width, this.y);
        this.c.lineTo(0, this.y);
        this.c.stroke()
        this.c.closePath()
    }
    this.update = function() {
        let parentWidth = $("#" + canvasId).parent().width();
        this.canvasObj.width = parentWidth;
        this.canvasObj.height = parentWidth;
        let dx = this.x - this.canvasObj.width/2;
        let dy = this.y - this.canvasObj.height/2;
        this.x = this.canvasObj.width/2;
        this.y = this.canvasObj.height/2;
        this.circleRadius = this.canvasObj.width / pointScale
        this.ratio = this.canvasObj.width/target_details[this.dist][5];
        this.targetBackground.update(this.x, this.y, this.canvasObj.width/2)
        for (let i=0; i<this.points.length; i++){
            this.points[i].update(this.points[i].x - dx, this.points[i].y - dy, this.circleRadius)
        }
    };
    let ThisTarget = this;
    //Change target dimensions if its parent div changes dimensions
    new ResizeSensor(canvasParent, function(){
        ThisTarget.update();
        ThisTarget.draw();
    });
    this.draw()
}
