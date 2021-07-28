function get_arr() {
    // var arr = JSON.stringify({'email':'tomb@raider.com','name':'LaraCroft'});
    // var data1 = new FormData()
    // data1.append('data1',arr)
    let xhr = new XMLHttpRequest();
    xhr.open('GET', 'upl_arr/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    // xhr.responseType = "application/json";
    xhr.onload = function (e) {

        if (this.status == 200) {
            // var json = JSON.parse( JSON.parse(xhr.response)['dat'] );
            var json = JSON.parse(xhr.response)
            const etalonJson = JSON.parse(JSON.stringify(json))
            // console.log(json)
            genMain(json)

            let sb_chast = document.getElementById('sb_ch')

            sb_chast.addEventListener('click', function () {
                json = dump_ch(json, etalonJson)
                genMain(json)

                // console.log(json)

            })

            let sb_product = document.getElementById('sb_pr')

            sb_product.addEventListener('click', function () {
                // console.log(etalonJson)
                arr_keys = document.querySelectorAll("[data-title='1']")
                json = dump_prod(json, etalonJson, arr_keys)
                genMain(json)

            })


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
                        console.log(this.response)
                    }
                }

                xhr.send(data1);


            })

        } else {
        }
    }
    // xhr.onerror = function (ev){
    //     alert('Формирование заверщилось ошибкой')
    // }

    xhr.send();

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
        inp.value = json[key][0]
        inp.setAttribute('data-path', [key])

        inp.addEventListener('blur', function (e) {
            let targ = e.target
            json[targ.getAttribute('data-path')][0] = targ.value
            // console.log(json)
        })

        let str_ = document.createElement('a')
        str_.textContent = '/' + json[key][1]

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
            inp.value = json[key____][key][0]
            inp.setAttribute('data-path', [val_ch, key____, 0,key])

            inp.addEventListener('blur', function (e) {
                let targ = e.target
                let arr = inp.getAttribute('data-path').split(',')
                global_json[arr[0]][2][arr[1]][arr[3]][arr[2]] = targ.value
                // console.log(global_json)
            })

            let str__ = document.createElement('a')
            str__.textContent = '/' + json[key____][key][1]
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
                inp__.value = json[key____][key][2][key_][0]
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
                    str___.textContent = '/' + json[key____][key][2][key_][1]
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





