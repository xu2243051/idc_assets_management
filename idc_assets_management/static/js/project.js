/* Project specific Javascript goes here. */

// add attribute required to the element with class required
// // because bootstrap don't has class required
$('.required').attr('required', 'required');
$(".required").find("input").attr('required', 'required');

function showinfo(text, css_class){
    $("#results p").empty();
    $("#results p").append(text);
    $("#results").addClass(css_class).fadeIn();
}

//关闭页面内容上部的提示信息
$("#close_results").click(function(){
    $("#results").fadeOut();
});

// 获取选中的复选框
function get_checked(){
    var items=$(':checkbox:checked');
    
    if(items.length <= 0){
        showinfo('你需要至少选择一个选项！', 'alert-error');
        return 0;
    }
    else
    {
        return items;
    }
}



// set csrf for django
// https://docs.djangoproject.com/en/1.5/ref/contrib/csrf/#ajax
var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


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


var buttonPress = function()
    {
        click_button.disabled=true;
        command_value = click_button.attributes["command"].nodeValue
        $.ajax({data:{command:command_value , pk:'1', data:'asdf'},
            dataType: "Text", error: registerError,
            success: regiterSuccess, type: "POST", 
            url: location.href});
    };

var registerError_forchecked = function(XMLHttpRequest, textStatus, errorThrown)
    {
        showinfo(errorThrown, 'error');
        items_count--;
    };
var regiterSuccess_forchecked = function(data, textStatus, XMLHttpRequest)
    {
        items_count--;
        var data_json = JSON.parse(data);
        $("#"+data_json.pk).text(data_json.result);

        $("#"+data_json.pk).parents('tr').removeClass('info');
    };

//类为command的按钮的click操作的函数
$(".server_command").click(function(){
    //上面3个函数中的click_button 都是这里定义的
    //尝试过直接在当前函数中开关按钮，失败了，并不会等待ajax成功才enable按钮

    click_button = this;
    command_value = click_button.attributes["command"].nodeValue

    // 获得点击的按钮所在的btn-group，并且使得这个组不能点击，等所有行的ajax执行完成才恢复
    btn_group = $("[command="+ command_value +"]").parents('ul').siblings("button");
    btn_group.attr('disabled',true );

    items = get_checked();
    items_count = items.length
    if (items == 0 ){
        //如果没有选择checkbox，items的值为0， 退出当前的函数
        return 0
    }
    // 判断是否更新
    if (confirm(this.innerHTML+ '\r' + '你选择了 '+ items_count +' 行')){
        if (items){
            for (i=0; i<items.length; i++){
                // pk, row 是全局变量，所以在循环的过程中会改变，所以ajax的成功函数无法正常使用这两个变量
                pk = items[i].value;
                row = $("#"+pk).parents("tr");
                row.addClass('info');
                //$("#"+pk).text('test-td');
                $.ajax({data:{command:command_value , pk:pk, data:'asdf'},
                    dataType: "Text", error: registerError_forchecked,
                    success: regiterSuccess_forchecked, type: "POST",
                    url: location.href});
            }
        }
    }

    setInterval(function(){check_items_finish()}, 1000)
    
    
    event.preventDefault();
});

function sleep(milliSeconds){
    var startTime = new Date().getTime(); // get the current time
    while (new Date().getTime() < startTime + milliSeconds); //hold cpu
}

function check_items_finish(){
    if (items_count == 0){
        // 如果所有行的ajax执行完成，items_count的结果将会降为0
        btn_group.attr('disabled',false );
    }
}
