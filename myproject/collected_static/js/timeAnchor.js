function timeAnchor(time, type) {
    timesf = new Date(time)
    yyyy = timesf.getFullYear()
    mm = timesf.getMonth()
    dd = timesf.getDate()
    if (type=='year') {
        st = new Date(yyyy,0,1,0,0,-1)
        et = new Date(yyyy+1,0,1,0,0,0)
        start = st.toISOString()
        end = et.toISOString()
    } else if (type=='month') {
        st = new Date(yyyy,mm,1,0,0,-1)
        et = new Date(yyyy,mm+1,1,0,0,0)
        start = st.toISOString()
        end = et.toISOString()
    } else {
        st = new Date(yyyy,mm,dd,0,0,-1)
        et = new Date(yyyy,mm,dd+1,0,0,0)
        start = st.toISOString()
        end = et.toISOString()
    }
    return [start, end]
}