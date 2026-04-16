use criterion::{black_box, criterion_group, criterion_main, Criterion};
use eml_sr::{SearchConfig, Searcher};

fn bench_sin_search(c: &mut Criterion) {
    let xs: Vec<f64> = (0..20).map(|i| i as f64 * 0.3).collect();
    let ys: Vec<f64> = xs.iter().map(|&x| x.sin()).collect();

    let config = SearchConfig::builder()
        .max_complexity(4)
        .precision_goal(1e-10)
        .build();
    let searcher = Searcher::new(config);

    c.bench_function("search_sin_x", |b| {
        b.iter(|| {
            let _ = searcher.find_function(black_box(&xs), black_box(&ys));
        })
    });
}

criterion_group!(benches, bench_sin_search);
criterion_main!(benches);
