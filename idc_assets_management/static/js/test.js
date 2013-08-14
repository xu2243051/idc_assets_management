/* Project specific Javascript goes here. */

var registerError = function(XMLHttpRequest, textStatus, errorThrown)
    {
        showinfo(errorThrown);
        click_button.disabled=false;
        //$("#test").attr("disabled", "disabled");
    };

var regiterSuccess = function(data, textStatus, XMLHttpRequest)
    {
        click_button.disabled=false;
        showinfo(data);
    };

$(".testcommand").click(function(){
    //上面3个函数中的click_button 都是这里定义的
    //尝试过直接在当前函数中开关按钮，失败了，并不会等待ajax成功才enable按钮
    click_button = this;
    buttonPress();
});
//类为command的按钮的click操作的函数
