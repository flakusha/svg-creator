
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod image_analysis;
use image_analysis::analyze_image;


#[pyfunction]
/// Function takes Blender3D RGB representation of rendered and
/// loaded-into-editor image which is then converted into String to avoid
/// wasting time to send List and then downcast every component into desired
/// data structure/type. This function takes the String of floats with 6f
/// preicsion: `"0.123456 0.456789 0.891011 ..."` as an
/// RGB floating-point image, although integers are also possible.
///
/// Then 9-pixel window moves along the image to get all possible indexed
/// colors and their neighbours. 0 (black) and 1 (white) pixels and
/// their 9-pixel chunks are ignored for
/// 8 and 16 bit images, for 32 bit images only black color is ignored.
///
/// After all neighbours are found non-neighbours stage starts, resulting output
/// format is:
///
/// ```norun
/// "
/// 0.121314 0.343536 0.565758: 0.676869 0.899010 0.121314,
/// 0.232425 0.343536 0.565758, ...\n
/// 0.212223 0.434445 0.656667: 0.767879 0.080910 0.212223, ...\n ...
/// "
/// ```
///
/// This String is reconstructed into task list for tracing later.
pub fn analyze_image_colors(py: Python, image: String, w: usize, h: usize,
mode: &str, max_num_colors: usize) -> PyResult<String> {
    Ok(analyze_image(image, w, h, mode, max_num_colors))
}


#[pymodule]
pub fn svg_creator_rs(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(analyze_image_colors, m)?)?;

    Ok(())
}


// #[cfg(test)]
// mod tests {
//     #[test]
//     fn it_works() {
//         assert_eq!(2 + 2, 4);
//     }
// }
