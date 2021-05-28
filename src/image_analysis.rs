// use std::slice::windows;
// use std::{collections::HashSet, thread};
use std::{sync::{Arc, }};
use rayon::ThreadPoolBuilder;
use dashmap::{DashMap, DashSet};

// Black and white pixels and chunks to be ignored in 8- and 16-bit modes
const PXB: &str = "0.000000 0.000000 0.000000";
const PXW: &str = "1.000000 1.000000 1.000000";
const CHB: [&str; 9] = [PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB];
const CHW: [&str; 9] = [PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW];

pub fn analyze_image(image: String, w: usize, h: usize, mode: &'static &str,
    max_num_colors: usize) -> String {
    // Image formatted for further usage
    let mut imgr = Vec::<&str>::with_capacity(w * h);
    convert_image(image, &mut imgr);

    let res = detect_colors(&imgr, w, h, &mode, max_num_colors);
    convert_result(res)
}

/// Converts image from Python String to Rust Vector of &str
fn convert_image(image: String, imgr: &mut Vec<&str>) {
    let mut rgb_temp = Vec::<&str>::with_capacity(3);

    for pxc in image.split_whitespace() {
        if rgb_temp.len() < 3 {
            rgb_temp.push(pxc);
        } else {
            imgr.push(&rgb_temp.join(" "));
            rgb_temp.clear();
            rgb_temp.push(pxc);
        }
    }
}

fn detect_colors(imgr: &'static Vec<&str>, w: usize, h: usize,
mode: &'static &str, max_num_colors: usize)
-> DashMap<String, DashSet<String>> {
    // let kmax = w * h - 1;
    let task_pool = ThreadPoolBuilder::new()
        .num_threads(0).build().unwrap(); // Automatically detect num_threads
    let (tx, rx) = std::sync::mpsc::channel();
    let mut color_graph = Arc::new(
        DashMap::<String, DashSet<String>>::with_capacity(max_num_colors));
    

    for i in 1..h - 1 {
        for j in 1..w - 1 {
            let tx = tx.clone();
            task_pool.spawn(move || {
                tx.send(scan_window(&imgr, i, j, &w, &h, mode,
                color_graph)).unwrap();
            })
        }
    }

    drop(tx);

    let temp = Arc::new(
        DashMap::<String, DashSet<String>>::with_capacity(max_num_colors));
    Arc::try_unwrap(temp).unwrap()

}

/// Scans image using 3x3 windows
fn scan_window(img: &Vec<&str>, i: usize, j:usize, w: &usize, h: &usize,
mode: &str, color_graph: Arc<DashMap<String, DashSet<String>>>) {
    let c = [
        (i - 1) * w + j - 1, (i - 1) * w + j, (i - 1) * w + j + 1,
        i * w + j - 1,       i * w + j,       i * w + j + 1,
        (i + 1) * w + j - 1, (i + 1) * w + j, (i + 1) * w + j + 1,
    ];
    let window = [
        img[c[0]], img[c[1]], img[c[2]],
        img[c[3]], img[c[4]], img[c[5]],
        img[c[6]], img[c[7]], img[c[8]],
    ];

    let neigh = DashSet::with_capacity(8);
    for ct in 0..=9 {
        if ct != 4 {neigh.insert(window[ct].to_string());}
    }
    color_graph.insert(window[4].to_string(), neigh);
    
}

/// Converts HashMap of colors graph into String
fn convert_result(res: DashMap<String, DashSet<String>>) -> String {

}