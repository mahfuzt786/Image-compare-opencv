//jQuery(function ($) {
// // image gallery
// // init the state from the input
// $(".image-checkbox").each(function () {
//   if ($(this).find('input[type="checkbox"]').first().attr("checked")) {
//     $(this).addClass('image-checkbox-checked');
//   }
//   else {
//     $(this).removeClass('image-checkbox-checked');
//   }
// });

// // sync the state to the input
// $(".image-checkbox").on("click", function (e) {
//   $(this).toggleClass('image-checkbox-checked');
//   var $checkbox = $(this).find('input[type="checkbox"]');
//   $checkbox.prop("checked",!$checkbox.prop("checked"))

//   e.preventDefault();
// });
//});

    jQuery(function ($) {
        // init the state from the input
        // $(".image-checkbox").each(function () {
        //     if ($(this).find('input[type="checkbox"]').first().attr("checked")) {
        //         $(this).addClass('image-checkbox-checked');
        //     }
        //     else {
        //         $(this).removeClass('image-checkbox-checked');
        //     }
        // });

        // sync the state to the input
        $(".image-checkbox").on("click", function (e) {
            // if ($(this).hasClass('image-checkbox-checked')) {
            //     $(this).removeClass('image-checkbox-checked');
            //     $(this).find('input[type="checkbox"]').first().removeAttr("checked");
            // }
            // else {
            //     $(this).addClass('image-checkbox-checked');
            //     $(this).find('input[type="checkbox"]').first().attr("checked", "checked");
            // }
            //e.preventDefault();
            
            var trainSelected   = [];
            var posterSelected  = [];
            $('input[name="image"]:checked').each(function() {
                trainSelected.push($(this).val());
            });
            $('input[name="imageUp"]:checked').each(function() {
                posterSelected.push($(this).val());
            });

            if(trainSelected.length > 0 && posterSelected.length > 0)
            {
                $('#btnStart').show();
                $('#btnStartDis').hide();
            }
            else {
                $('#btnStart').hide();
                $('#btnStartDis').show();
            }

            var trainJsonString     = JSON.stringify(trainSelected);
            var posterJsonString    = JSON.stringify(posterSelected);

            $('#trainSelected').val(trainJsonString);
            $('#posterSelected').val(posterJsonString);
            
        });
    });

