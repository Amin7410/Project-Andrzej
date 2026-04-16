//! The `core` module: fundamental data types shared by all other modules.
//!
//! Nothing in `core` depends on the search engine or operator registry —
//! it defines only the data structures that everything else builds upon.

pub mod expression;
pub mod signature;
pub mod value;
