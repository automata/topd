;; topd.scm :: a simple (scheme) interface to puredata

;; WARNING! it's a crap, unfinished hack...

;; execute "pd recebe.pd &" and try this on your repl:
;; (load "topd.scm")
;; (define patch (patch-connect "localhost" 3006))
;; (-> (osc~ 440 100 100) (dac~ 100 150))

(use tcp) ; to sockets
(use srfi-13) ; to string-join


;; patch

(define (patch-connect #!optional 
                       (filename "recebe.pd") 
                       (hostname "localhost")
                       (port 3006))
  (define-values (socket-input socket-output)
    (tcp-connect hostname port))
  `((filename ,filename) 
    (hostname ,hostname) 
    (port ,port) 
    (socket ,socket-output)
    (boxes ())
    (connections ())))

(define (patch-disconnect)
  (close-output-port (cadr (assoc 'socket patch))))

(define (patch-send command)
  (write-line (string-append "pd-" 
                             (cadr (assoc 'filename patch)) 
                             " " 
                             command 
                             ";") 
              (cadr (assoc 'socket patch))))

(define (pd-send command)
  (let ((socket (cadr (assoc 'socket patch))))
    (write-line (string-append "pd " 
                               command 
                               ";") 
                socket)))

(define (dsp state)
  (pd-send (space "dsp" (->string state))))

(define (editmode state)
  (patch-send (space "editmode" (->string state))))

;; boxes

(define (object-create label x y)
  (patch-send (space "obj" (->string x) (->string y) label))
  (let ((obj `(((box object) (id ,(+ 1 (length (cadr (assoc 'boxes patch)))))))))
    (set! (cadr (assoc 'boxes patch)) (append (cadr (assoc 'boxes patch)) obj))
    (car obj)))

;;FIXME: just object-create is working... i'm so tired to make the rest :-\
(define (message-create label x y)
  (patch-send (space "msg" (->string x) (->string y) label)))

(define (number-create x y)
  (patch-send (space "number" (->string x) (->string y))))

(define (symbol-create x y)
  (patch-send (space "symbol" (->string x) (->string y))))

(define (comment-create label x y)
  (patch-send (space "text" (->string x) (->string y) label)))

;; connections

;;FIXME: i have to store connections as i did for boxes... but i'm tired, right? ;-)
(define (connect source outlet target inlet)
  (patch-send 
   (space "connect"
          (->string source)
          (->string outlet)
          (->string target)
          (->string inlet)))
  (let ((con `(((id ,(+ 1 (length (cadr (assoc 'connections patch))))) 
                (source ,source) 
                (outlet ,outlet) 
                (target ,target) 
                (inlet ,inlet)))))
    (set! (cadr (assoc 'connections patch)) (append (cadr (assoc 'connections patch)) con))
    (car con)))

;; now begins the real fun! a DSL to patching...

(define (dac~ x y)
  (object-create "dac~" x y))

(define (osc~ freq x y)
  (object-create (space "osc~" (->string freq)) x y))

(define (-> source-box target-box)
  (connect (cadr (assoc 'id source-box))
           0 
           (cadr (assoc 'id target-box))
           0))


;; aux functions

(define (space . strings-list)
  "Joins the list of strings with a space between them."
  (string-join strings-list " "))

; always connect to "recebe.pd" patch
(define patch (patch-connect))
