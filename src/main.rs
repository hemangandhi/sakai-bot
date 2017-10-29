#![type_length_limit="2097152"]
extern crate tokio_core;
extern crate futures;
extern crate fantoccini;

use fantoccini::Client;
use fantoccini::error::CmdError;
use futures::prelude::*;

use std::fs::File;
use std::io::prelude::*;
use std::io::{BufReader, Error, ErrorKind};

fn read_cfg(path: &str) -> Result<(String, String), Error> {
    match File::open(path) {
        Ok(handle) => {
            let mut buf = BufReader::new(&handle);
            let mut lines = buf.lines();
            if let Some(Ok(net_id)) = lines.next() {
                if let Some(Ok(password)) = lines.next() {
                    return Ok((net_id, password));
                } else {
                    println!("Password not read!");
                    return Err(Error::new(ErrorKind::Other, "No password"));
                }
            } else {
                println!("NetID not read!");
                return Err(Error::new(ErrorKind::Other, "No net_id"));
            }
        },
        Err(ioe) => {
            println!("File troubles!");
            return Err(ioe);
        }
    };
}

fn main() {
    let mut core = match tokio_core::reactor::Core::new() {
        Ok(event_loop) => event_loop,
        _ => {
            println!("No Tokio or Tokyo!");
            return;
        }
    };

    let (c, fin) = Client::new("http://localhost:4444", &core.handle());
    let c = match core.run(c) {
        Ok(future_item) => future_item,
        Err(cli_err) => {
            println!("Error in client running! {}", cli_err);
            return;
        }
    };

    {
        let c = &c;

        let f = c.goto("https://sakai.rutgers.edu/portal")
            .and_then(move |_| c.current_url())
            .and_then(move |url| {
                println!("{}", url);
                c.by_selector("#loginLink1")
            })
            .and_then(|e| e.click())
            .and_then(|_| futures::done(read_cfg("my.config")
                                            .or_else(|err| Err(CmdError::Lost(err)))))
            .and_then(move |(net_id, pass)| {
                println!("Read in stuff");
                let js1 = format!("document.getElementById('username').value = '{}';\n", net_id);
                let js2 = format!("document.getElementById('password').value = '{}';\n", pass);
                let js = js1 + &js2;
                println!("Gonna JS: {}", js.as_str());
                c.execute(js.as_str(), vec![])
            })
            .and_then(move |_| c.by_selector(".btn-submit"))
            .and_then(|e| e.click())
            .and_then(move |_| c.current_url())
            .and_then(move |_| c.by_selector(".all-sites-label"))
            .and_then(|e| e.click())
            .and_then(move |_| c.current_url())
            .and_then(|url| {
                println!("Got to {}!", url);
                Ok(())
            });

        match core.run(f) {
            Ok(_) => println!("Ran!"),
            Err(run_err) => {
                println!("Couldn't run the thing! {}", run_err);
            },
        };
    }

    drop(c);
    match core.run(fin) {
        Ok(_) => println!("Finito!"),
        _ => println!("Errored on the last step.")
    }
}
