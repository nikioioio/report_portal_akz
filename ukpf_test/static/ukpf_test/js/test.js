var file_to_upl
var json_to_upl

//В данном модуле  происходит возаимодействие с backend отчета

function get_arr() {

    var control = document.getElementById("ctrl");
    var control2 = document.getElementById("ctrl2");
    var data2 = new FormData()
    file_to_upl = control.files[0]
    data2.append('uboi', file_to_upl)
    data2.append('zakaz', control2.files[0])
    // var arr = JSON.stringify({'email':'tomb@raider.com','name':'LaraCroft'});
    // var data1 = new FormData()
    // data1.append('data1',arr)
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'upl_arr/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    // xhr.responseType = "application/json";
    xhr.onload = function (e) {

        if (this.status == 200) {

            // file1 = _base64ToArrayBuffer(this.response['file1'])
            // var blob = new Blob([file1], { type: 'application/vnd.ms-excel' });
            //
            // var downloadUrl = URL.createObjectURL(blob);
            // var a = document.createElement("a");
            // a.href = downloadUrl;
            // a.download = 'uboi.xlsx';
            // document.body.appendChild(a);
            // a.click()

            // var json = JSON.parse( JSON.parse(xhr.response)['dat'] );
            var json = JSON.parse(xhr.response)
            const etalonJson = JSON.parse(JSON.stringify(json))
            // console.log(json)
            genMain(json)

            let sb_chast = document.getElementById('sb_ch')

            sb_chast.addEventListener('click', function () {
                json = dump_ch(json, etalonJson)
                genMain(json)

                // console.log(1)

            })

            let download_res = document.getElementById('download_res')

            download_res.addEventListener('click', function () {
                download()
                // console.log(1)
            })

            let download_table = document.getElementById('download_table')

            download_table.addEventListener('click', function () {
                download2()
                // console.log(1)
            })



            // let sb_product = document.getElementById('sb_pr')
            //
            // sb_product.addEventListener('click', function () {
            //     // console.log(etalonJson)
            //     arr_keys = document.querySelectorAll("[data-title='1']")
            //     json = dump_prod(json, etalonJson, arr_keys)
            //     genMain(json)
            //
            // })


            let upgrage_chast = document.getElementById('per_ch')


            upgrage_chast.addEventListener('click', function () {

                var data1 = new FormData()
                data1.append('data1',JSON.stringify(json))
                let xhr = new XMLHttpRequest();
                xhr.open('POST', 'update/');
                // xhr.setRequestHeader('Content-Type', "application/json");
                // xhr.responseType = "application/json";

                xhr.onload = function (e) {

                    if (this.status == 200) {
                        var json = JSON.parse(xhr.response)
                        json_to_upl = json
                        // const etalonJson = JSON.parse(JSON.stringify(json))
                        genMain(json)
                        // console.log(this.response)
                    }
                }

                xhr.send(data1);


            })

            let getTable = document.getElementById('get_table')

            getTable.addEventListener('click', function () {

                get_arr1()


            })

        } else {
        }
    }
    // xhr.onerror = function (ev){
    //     alert('Формирование заверщилось ошибкой')
    // }

    xhr.send(data2);

}


//обновляет json в соответсвтии с эталоном( часть "частей")
function dump_ch(json, etalon) {
    for (var key in json) {
        json[key][0] = etalon[key][0]
    }
    return json
}

function dump_prod(json, etalon, arr_keys) {

    arr_keys.forEach(function (item, i, arr) {
        for (var key in json) {

            for (key_ in json[key][2]){
                if (typeof json[key][2][key_][item.textContent] != "undefined") {
                    // json[key][2][key_][item.textContent] = etalon[key][2][key_][item.textContent]
                    json[key][2][key_][item.textContent][0] = parseInt(etalon[key][2][key_][item.textContent][0])

                    for (var p in etalon[key][2][key_][item.textContent][2]){
                        json[key][2][key_][item.textContent][2][p][0] = parseInt(etalon[key][2][key_][item.textContent][2][p][0])
                    }

                    // console.log(etalon[key][2][key_][item.textContent][2])
                    // json[key][2][0] = etalon[key][2][0]
                }
            }

        }

    })

    return json

}


function genMain(json) {
    $('.one').remove()
    $('.two').remove()

    for (var key in json) {
        let but = document.createElement('button');

        but.onclick = function () {
            genProduct(json[but.textContent][2], but.textContent, json)
        }
        but.textContent = key

        let inp = document.createElement('input');
        inp.className = 'size'
        inp.value = json[key][0].toLocaleString('ru')
        let arrrrr_ = ["Грудка", "Четвертина", "ЦБ"]
        if(arrrrr_.indexOf( key ) == -1){
            inp.setAttribute('disabled', 'disabled')
        }

        inp.setAttribute('data-path', [key])

        inp.addEventListener('blur', function (e) {
            let targ = e.target
            json[targ.getAttribute('data-path')][0] = targ.value
            // console.log(json)
        })

        let str_ = document.createElement('a')
        str_.textContent = '/ ' + json[key][1].toLocaleString('ru')

        if(parseInt(json[key][0])<parseInt(json[key][1])){
            inp.style.backgroundColor = "mistyrose"
            str_.style.backgroundColor = "mistyrose"
        }


        let div_ = document.createElement('div');
        div_.className = 'one'
        div_.appendChild(but)
        div_.appendChild(inp)
        div_.appendChild(str_)

        $('#left').append(div_)

    }

    // let div__ = document.createElement('div');
    // div__.className = 'two'

    // let per_ch = document.createElement('button');
    // per_ch.textContent = 'Перерасчитать части'
    //
    // let sb_chast = document.createElement('button');
    // sb_chast.textContent = 'Сбросить части'
    // sb_chast.id = 'sb_ch'

    // sb_chast.addEventListener('click',function (e){
    //
    // })

    // div__.appendChild(per_ch)
    // div__.appendChild(sb_chast)

    // $('#left').append(div__)

}

function genProduct(json, val_ch, global_json) {
    // console.log(val_ch)
    $('.three').remove()

    for (var key____ in json) {
        for (var key in json[key____]) {
            let str_ = document.createElement('a')
            str_.textContent = key
            str_.style.fontWeight = "bold"
            str_.setAttribute('data-title', 1)

            let div_ = document.createElement('div');
            div_.className = 'three'

            let inp = document.createElement('input');
            inp.className = 'size'
            inp.value = json[key____][key][0].toLocaleString('ru')
            inp.setAttribute('data-path', [val_ch, key____, 0,key])

            inp.addEventListener('blur', function (e) {
                let targ = e.target
                let arr = inp.getAttribute('data-path').split(',')
                global_json[arr[0]][2][arr[1]][arr[3]][arr[2]] = targ.value
                // console.log(global_json)
            })

            let str__ = document.createElement('a')
            str__.textContent = '/ ' + json[key____][key][1].toLocaleString('ru')
            if(parseInt(json[key____][key][0])<parseInt(json[key____][key][1])){
                inp.style.backgroundColor = "mistyrose"
                str__.style.backgroundColor = "mistyrose"
            }
            div_.appendChild(str_)
            div_.appendChild(inp)
            div_.appendChild(str__)
            $('#right').append(div_)


            for (var key_ in json[key____][key][2]) {


                let str__ = document.createElement('a')
                str__.textContent = key_
                // console.log(key_)

                let div__ = document.createElement('div');
                div__.className = 'three'

                let inp__ = document.createElement('input');
                inp__.className = 'size'
                inp__.value = json[key____][key][2][key_][0].toLocaleString('ru')
                inp__.setAttribute('data-path', [val_ch, key, key_, 0, key____])

                inp__.addEventListener('blur', function (e) {
                    let targ = e.target
                    let arr = inp__.getAttribute('data-path').split(',')
                    global_json[arr[0]][2][arr[4]][arr[1]][2][arr[2]][0] = targ.value
                })

                let str___ = document.createElement('a')
                if (typeof json[key____][key][2][key_][1] == "undefined") {
                    str___.textContent = ''
                } else {
                    str___.textContent = '/ ' + json[key____][key][2][key_][1].toLocaleString('ru')
                    if(parseInt(json[key____][key][2][key_][0])<parseInt(json[key____][key][2][key_][1])){
                        inp__.style.backgroundColor = "mistyrose"
                        str___.style.backgroundColor = "mistyrose"
                    }
                }

                div__.appendChild(str__)
                div__.appendChild(inp__)
                div__.appendChild(str___)
                //
                //
                $('#right').append(div__)
            }


        }


        // let div___ = document.createElement('div');
        // div___.className = 'three'
        //
        // let per_pr = document.createElement('button');
        // per_pr.textContent = 'Перерасчитать продукты'
        //
        // let sb_prod = document.createElement('button');
        // sb_prod.textContent = 'Сбросить продукты'
        // div___.appendChild(per_pr)
        // div___.appendChild(sb_prod)
        // $('#right').append(div___)


    }
}

function download(){

    // console.log(5)
    var data = new FormData()
    // data.append('file', file_to_upl)
    data.append('json', json_to_upl)
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'upl_test/');
    xhr.responseType = 'arraybuffer';
    // xhr.setRequestHeader('Content-Type', "application/json");
    // xhr.responseType = "application/json";

    xhr.onload = function (e) {
        if (this.status == 200) {

            let disposition = this.getResponseHeader('Content-Disposition')
            if (disposition && disposition.indexOf('attachment') !== -1) {
                let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                let matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var blob = new Blob([this.response], { type: 'application/vnd.ms-excel' });
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            alert('Результат готов')
        } else {
            alert('Ошибка')

            function arrayBufferToString(buffer, encoding) {
                return new Promise((resolve, reject) => {

                    var blob = new Blob([buffer], {type: 'text/plain'});
                    var reader = new FileReader();
                    reader.readAsText(blob, encoding);
                    reader.onload = (ev) => {
                        if (ev.target) {
                            resolve(ev.target.result)
                        } else {
                            reject(new Error('Could not convert string to string!'));
                        }
                    }
                })

            }

            arrayBufferToString(this.response, 'UTF-8').then((r) => {
                var decoder = new TextDecoder('utf-8')
                message = JSON.parse(r)['error']
                message1 = JSON.parse(r)['error1']
                // console.log(message)
                $('body').append('<article class="trace">' + message + '</article>').css({'fontsize': '24px'})
                // $('body').append('<article class="trace">'+message1+'</article>').css({'fontsize':'24px'})
                // alert(message)
            })

            // Materialize.toast('Invalid data!', 2000)
        }
    }
    xhr.send(data);
}

function download2(){

    // console.log(5)
    var data = new FormData()
    // data.append('file', file_to_upl)
    data.append('json', json_to_upl)
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'upl_test2/');
    xhr.responseType = 'arraybuffer';
    // xhr.setRequestHeader('Content-Type', "application/json");
    // xhr.responseType = "application/json";

    xhr.onload = function (e) {
        if (this.status == 200) {

            let disposition = this.getResponseHeader('Content-Disposition')
            if (disposition && disposition.indexOf('attachment') !== -1) {
                let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                let matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var blob = new Blob([this.response], { type: 'application/vnd.ms-excel' });
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            alert('Результат готов')
        } else {
            alert('Ошибка')

            function arrayBufferToString(buffer, encoding) {
                return new Promise((resolve, reject) => {

                    var blob = new Blob([buffer], {type: 'text/plain'});
                    var reader = new FileReader();
                    reader.readAsText(blob, encoding);
                    reader.onload = (ev) => {
                        if (ev.target) {
                            resolve(ev.target.result)
                        } else {
                            reject(new Error('Could not convert string to string!'));
                        }
                    }
                })

            }

            arrayBufferToString(this.response, 'UTF-8').then((r) => {
                var decoder = new TextDecoder('utf-8')
                message = JSON.parse(r)['error']
                message1 = JSON.parse(r)['error1']
                // console.log(message)
                $('body').append('<article class="trace">' + message + '</article>').css({'fontsize': '24px'})
                // $('body').append('<article class="trace">'+message1+'</article>').css({'fontsize':'24px'})
                // alert(message)
            })

            // Materialize.toast('Invalid data!', 2000)
        }
    }
    xhr.send(data);
}

function get_arr1() {
    var arr = JSON.stringify(json_to_upl);
    // console.log(json_to_upl)
    var data1 = new FormData()
    data1.append('data1', arr)
    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'get_table/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    // xhr.responseType = "application/json";
    xhr.onload = function (e) {

        if (this.status == 200) {
            $('.table_dark').remove()
            let json = JSON.parse(xhr.response)

            let table = document.createElement('table');

            table.className = 'table_dark'

            for (let key in json) {
                let tr = document.createElement('tr');
                if (key > 0) {
                    for (let key_ in json[key]) {
                        // console.log(json[key][key_])
                        let td = document.createElement('td');
                        // console.log(key, key_, json[key][key_])
                        // console.log(json[key][key_])
                        if(json[key][key_]=='в т.ч. Заявка'){
                            td.textContent = 'в т.ч. Заявка'
                        }
                        if(json[key][key_]=='в т.ч. Остатки'){
                            td.textContent = '  в т.ч. Остатки'
                        }
                        td.textContent = json[key][key_]
                        tr.appendChild(td)
                    }

                }else{
                    for (let key_ in json[key]) {
                        // console.log(json[key][key_])
                        let th = document.createElement('th');
                        th.textContent = json[key][key_]
                        tr.appendChild(th)
                    }

                }


            table.appendChild(tr)

                // console.log(json[key])
            }


            $('.intro__inner').append(table)

        } else {
        }
    }
    // xhr.onerror = function (ev){
    //     alert('Формирование заверщилось ошибкой')
    // }

    xhr.send(data1);

}




