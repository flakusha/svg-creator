// use std::slice::windows;
// use std::{collections::HashSet, thread};
use std::{ops::IndexMut, sync::{Arc, }};
use rayon::ThreadPoolBuilder;
use dashmap::{DashMap, DashSet};

// Black are to be ignored
const PXB: &str = "0.000000 0.000000 0.000000";
// const PXW: &str = "1.000000 1.000000 1.000000";
const CHB: [&str; 9] = [PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB];
// const CHW: [&str; 9] = [PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW];

/// Picks up information from Python and analyzes the image
pub fn analyze_image(image: &'static str, w: usize, h: usize,
mode: &'static &str, max_num_colors: usize) -> String {
    if !(w > 2 && h > 2) {
        return "".to_string();
    }

    // Image formatted for further usage
    let mut imgr = Vec::<&str>::with_capacity(w * h);
    convert_image(image, &mut imgr);

    let res = detect_colors(&imgr, w, h, &mode, max_num_colors);
    let res = detect_non_neighbours(res);
    convert_result(res)
}

/// Converts image from Python String to Rust Vector of &str
fn convert_image(image: &str, imgr: &mut Vec<&str>) {
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

/// Function spawns ThreadPool and tasks to check image and returns every color
/// and it's neighbouring pixels
fn detect_colors(imgr: &'static Vec<&str>, w: usize, h: usize,
mode: &'static &str, max_num_colors: usize)
-> DashMap<String, DashSet<String>> {
    // let kmax = w * h - 1;
    let task_pool = ThreadPoolBuilder::new()
        .num_threads(0).build().unwrap(); // Automatically detect num_threads
    let (tx, rx) = std::sync::mpsc::channel();
    let mut color_graph = Arc::new(
        DashMap::<String, DashSet<String>>::with_capacity(max_num_colors));

    // Ignore 1 pixel margin of the image
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

    // let temp = Arc::new(
    //     DashMap::<String, DashSet<String>>::with_capacity(max_num_colors));
    // Arc::try_unwrap(temp).unwrap()
    Arc::try_unwrap(color_graph).unwrap()
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

    // Center of the image window and neighbouring pixels
    let windowc = window[4].to_string();
    let neigh = DashSet::with_capacity(8);
    let mut ibp = 0;
    for ct in 0..=9 {
        if ct != 4 {
            neigh.insert(window[ct].to_string());
            if window[ct] == PXB {ibp += 1;}
        }
    }

    // Ignore black pixels and case every neighbouring pixel is black
    if windowc == PXB || ibp == 8 {
        return;
    }

    if color_graph.contains_key(&windowc) {
        let cgk = color_graph.get_mut(&windowc)
        .as_deref_mut().unwrap();
        for st in neigh.into_iter() {
            cgk.insert(st);
        }
    } else {
        color_graph.insert(windowc, neigh);
    }
}

fn detect_non_neighbours(color_graph: DashMap<String, DashSet<String>>) ->
DashMap<String, DashSet<String>> {
    let res = DashMap::<String, DashSet<String>>::with_capacity(
        color_graph.len());
    let processed = DashSet::<String>::with_capacity(color_graph.len());

    // Central and neighboring pixels
    for (pxc0, pxns0) in color_graph.into_iter() {
        for (pxc1, pxns1) in color_graph.into_iter() {
            if pxc0 != pxc1 && !processed.contains(&pxc0) {
                if !pxns1.contains(&pxc0) {
                    if !res.contains_key(&pxc0) {
                        res.insert(pxc0, DashSet::new());
                    }
                    res.get_mut(&pxc0).unwrap().insert(pxc1);
                }
            }
        if !res.contains_key(&pxc0) {
            // In case neighbours always found this color goes to graph alone
            // without any information in corresponding value, String type is
            // allocated for type compatibility
            res.insert(pxc0, DashSet::<String>::with_capacity(0));
        }
        processed.insert(pxc0);
        }
    }

    res
}

/// Converts HashMap of colors graph into String
fn convert_result(color_graph: DashMap<String, DashSet<String>>) -> String {
    let mut res = Vec::<String>::with_capacity(color_graph.len());

    for (pxc, pxn) in color_graph.into_iter() {
        res.push(format!("{}: {}", pxc, pxn.into_iter()
        .collect::<Vec<String>>().join(" ")));
    }

    res.join("\n")
}