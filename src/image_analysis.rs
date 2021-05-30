// use std::slice::windows;
use std::collections::{HashMap, HashSet};
use std::{sync::{Arc, }};
use rayon::ThreadPoolBuilder;
use dashmap::{DashMap, DashSet};

// Black are to be ignored
const PXB: &str = "0.000000 0.000000 0.000000";
// const PXW: &str = "1.000000 1.000000 1.000000";
const WIB: [&str; 9] = [PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB, PXB];
// const WIW: [&str; 9] = [PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW, PXW];

/// Picks up information from Python and analyzes the image for set of pixels
/// and
pub fn analyze_image(image: String, w: usize, h: usize, max_num_colors: usize) -> String {
    if !(w > 2 || h > 2) {
        return "".to_string();
    }

    // Image formatted for further usage
    let mut imgr = Vec::<String>::with_capacity(w * h);
    convert_image(&image, &mut imgr);

    let res = detect_colors(&imgr, w, h, max_num_colors);
    let res = detect_non_neighbours(res);
    convert_result(res)
}

/// Converts image from Python String to Rust Vector of &str
fn convert_image(image: &str, imgr: &mut Vec<String>) {
    let mut rgb_temp = Vec::<String>::with_capacity(3);

    for pxc in image.split_whitespace() {
        if rgb_temp.len() < 3 {
            rgb_temp.push(pxc.to_string());
        } else {
            let rgb_tempc = rgb_temp.clone().join(" ");
            imgr.push(rgb_tempc);
            rgb_temp.clear();
            rgb_temp.push(pxc.to_string());
        }
    }
}

/// Function spawns ThreadPool and tasks to check image and returns every color
/// and it's neighbouring pixels
fn detect_colors(imgr: &Vec<String>, w: usize, h: usize,
max_num_colors: usize)
-> DashMap<String, DashSet<String>> {
    let task_pool = ThreadPoolBuilder::new()
        .num_threads(0).build().unwrap(); // Automatically detect num_threads
    let (tx, _rx) = std::sync::mpsc::channel();
    let color_graph = Arc::new(
        DashMap::<String, DashSet<String>>::with_capacity(max_num_colors));

    // Ignore 1 pixel margin of the image
    for i in 1..h - 1 {
        for j in 1..w - 1 {
            let tx = tx.clone();
            let imgrc = imgr.clone();
            let cg = color_graph.clone();
            task_pool.spawn(move || {
                tx.send(scan_window(imgrc, i, j, &w, cg)).unwrap();
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
fn scan_window(img: Vec<String>, i: usize, j: usize, w: &usize,
color_graph: Arc<DashMap<String, DashSet<String>>>) {
    let c: [usize; 9] = [
        (i - 1) * w + j - 1, (i - 1) * w + j, (i - 1) * w + j + 1,
        i * w + j - 1,       i * w + j,       i * w + j + 1,
        (i + 1) * w + j - 1, (i + 1) * w + j, (i + 1) * w + j + 1,
    ];
    let window = [
        &img[c[0]], &img[c[1]], &img[c[2]],
        &img[c[3]], &img[c[4]], &img[c[5]],
        &img[c[6]], &img[c[7]], &img[c[8]],
    ];

    let windowc = window[4].to_string();
    if window == WIB || windowc == PXB {return;}

    let neigh = DashSet::with_capacity(8);
    if color_graph.contains_key(&windowc) {
        let cgk = color_graph.get(&windowc).unwrap();
        for st in neigh.into_iter() {
            cgk.insert(st);
        }
    } else {
        color_graph.insert(windowc, neigh);
    }
}

/// Takes px -> {px_neighbours} DashMap and converts it to
/// px -> {px_non_neighbours} HashMap
fn detect_non_neighbours(color_graph: DashMap<String, DashSet<String>>) ->
HashMap<String, HashSet<String>> {
    let cap = color_graph.len();
    let mut res = HashMap::<String, HashSet<String>>::with_capacity(cap);
    let processed = HashSet::<String>::with_capacity(cap);

    // Convert input into Vec so it's possible later to re-iterate several times
    let cgt = color_graph.into_iter()
    .map(|(a, b)| (a, b.into_iter().collect::<HashSet<String>>()))
    .collect::<Vec<(String, HashSet<String>)>>();

    // Take the key-value pair and check key against another key-value pairs
    for i in 0..cap {
        // Nested loop
        // let mut j = 0;
        let mut pxc0 = String::new();
        // let mut pxns0 = HashSet::<String>::new();
        for (j, (key, val)) in cgt.iter().enumerate() {
            if (i == j) && !processed.contains(key)  {
                pxc0 = key.clone();
                // pxns0 = *val;
            } else {
                if !val.contains(&pxc0) {
                    match res.contains_key(&pxc0) {
                        true => {
                            res.get_mut(&pxc0).unwrap().insert(key.clone());
                        },
                        false => {
                            // Temp DashSet allocation, cannot allocate and 
                            // insert at the same time
                            let mut dst = HashSet::<String>::with_capacity(16);
                            dst.insert(key.clone());
                            // Have to clone, to avoid move()
                            res.insert(pxc0.clone(), dst);},
                    }
                }
            }
        }
    }

    res
}

/// Converts HashMap of colors graph into String
fn convert_result(color_graph: HashMap<String, HashSet<String>>) -> String {
    let mut res = Vec::<String>::with_capacity(color_graph.len());

    for (pxc, pxn) in color_graph.into_iter() {
        res.push(format!("{}: {}", pxc,
        // There is more effective way without collecting to Vector
        pxn.into_iter().collect::<Vec<String>>().join(" ")));
    }

    return res.join("\n");
}
