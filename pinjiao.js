var doc = document.querySelector("#iframeautoheight").contentDocument;
var l = doc.querySelector("#pjkc").length;
console.log("评教项目数量",l);
document.querySelector("#iframeautoheight").onload = function () {
    var doc = document.querySelector("#iframeautoheight").contentDocument;
    if(doc.querySelector("#pjkc").lastElementChild == doc.querySelector("#pjkc>option[selected=selected]")){
        document.querySelector("#iframeautoheight").onload = null;
        doc.querySelector("#Button2").click();
    }
    console.log("加载完成。。")
    doing(doc)
};
var finish = 0;
function doing(doc) {
    console.log("正在评教",doc.querySelector("#pjkc>option[selected=selected]").innerText);
    doc.querySelectorAll("#DataGrid1 select").forEach(function (item) {
        var i = Math.ceil(Math.random() * 2);
        item.options[i].selected = true;
    });
    doc.querySelectorAll("#dgPjc select").forEach(function (item) {
        var i = Math.ceil(Math.random() * 2);
        item.options[i].selected = true;
    });
    finish ++;
    doc.querySelector("#Button1").click()
}
doing(doc);
// 全选复制到浏览器控制台 需要提前打开评教页面