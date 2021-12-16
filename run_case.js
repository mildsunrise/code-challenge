#!/usr/bin/env node

const fs = require('fs')
const readline = require('readline')
const child_process = require('child_process')

const CSI = '\u001b['
const SGR = (x = '') => `${CSI}${x}m`

const args = process.argv.slice(2)
if (args.length !== 2) {
    console.error('Usage: <script> <case name>')
    process.exit(1)
}
const [scrname, casename] = args

const scrFn = `${__dirname}/${scrname}.py`
const inFn = `${__dirname}/case/${scrname}.${casename}.in.txt`
const outFn = `${__dirname}/case/${scrname}.${casename}.out.txt`
const refFn = `${__dirname}/case/${scrname}.${casename}.ref.txt`

const inFd = fs.openSync(inFn)
const refFile = fs.createReadStream(refFn)
const outFile = fs.createWriteStream(outFn)

const proc = child_process.spawn(scrFn, [], {
    stdio: [inFd, 'pipe', 'inherit'],
})
fs.closeSync(inFd)

proc.stdout.pipe(outFile)

const outRl = readline.createInterface({ input: proc.stdout })
const refRl = readline.createInterface({ input: refFile })

async function readLines() {
    const outIt = (async function *() {
        for await (const line of outRl) {
            if (line.startsWith('Case '))
                yield line
            else
                console.log(line)
        }
    }())
    const refIt = refRl[Symbol.asyncIterator]()
    while (true) {
        const outRes = await outIt.next()
        const refRes = await refIt.next()
        if (outRes.done !== refRes.done)
            process.exit(1)
        if (outRes.done) break
        console.log(SGR(32) + refRes.value + SGR())
        if (outRes.value !== refRes.value)
            console.log(SGR(31) + outRes.value + SGR())
        console.log()
    }
}
readLines()

proc.on('exit', (code, signal) => {
    if (signal)
        throw Error(`script killed with ${signal}`)
    if (code)
        process.exit(code)
})
